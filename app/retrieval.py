"""In-process retrieval over the knowledge_sources/ corpus (CONTRACTS §2.2).

Loads reference documents (.md / .txt / .pdf), splits them into section /
paragraph chunks, and serves the most relevant chunks for a query via **BM25**
lexical ranking. No external service, vector DB, or embedding API — it is
deterministic, offline, and quota-free, which suits large/growing libraries and
a free-tier LLM key. The `search_knowledge` tool calls :func:`search`; the model
forms the query.

To add knowledge: drop files into ``backend/knowledge_sources/`` (or the folder
in ``KNOWLEDGE_DIR``) and restart, or call ``POST /api/reindex``.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .config import settings

# Default corpus folder: backend/knowledge_sources
_DEFAULT_DIR = Path(__file__).resolve().parent.parent / "knowledge_sources"

_READABLE_SUFFIXES = {".md", ".markdown", ".txt", ".text", ".pdf"}
_MAX_CHUNK_CHARS = 1400
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_K1 = 1.5
_B = 0.75

# Small stop list — common words that add noise to lexical scoring.
_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "at", "by",
    "is", "are", "be", "as", "with", "from", "this", "that", "it", "its", "if",
    "will", "shall", "may", "can", "such", "any", "all", "not", "no", "do",
    "does", "their", "they", "them", "i", "you", "your", "we", "our", "he",
    "she", "his", "her", "which", "who", "what", "when", "how", "where", "into",
    "out", "up", "down", "over", "under", "per", "via", "than", "then", "but",
    "so", "also", "etc", "e", "g", "ie",
}


def _knowledge_dir() -> Path:
    configured = settings.KNOWLEDGE_DIR.strip()
    return Path(configured).expanduser() if configured else _DEFAULT_DIR


def _tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 1 and t not in _STOP]


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def _looks_like_heading(paragraph: str) -> bool:
    """Heuristic: markdown heading, or a short title-like line (no period)."""
    if re.match(r"#{1,6}\s", paragraph):
        return True
    if "\n" in paragraph:
        return False
    return (
        len(paragraph) <= 90
        and len(paragraph.split()) <= 12
        and not paragraph.endswith(".")
        and bool(re.match(r"[A-Z0-9\"'“]", paragraph))
    )


def chunk_document(source: str, text: str) -> list[dict]:
    """Split a document into ``{source, title, text}`` chunks.

    Splits on blank lines into paragraphs, tracks the nearest heading as the
    chunk ``title``, and caps chunk size at ~``_MAX_CHUNK_CHARS`` so retrieval
    returns focused passages (e.g. a single T&C clause or definition).
    """
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: list[dict] = []
    title = source
    cur: list[str] = []
    cur_len = 0

    def flush() -> None:
        nonlocal cur, cur_len
        body = "\n\n".join(cur).strip()
        if body:
            chunks.append({"source": source, "title": title, "text": body})
        cur, cur_len = [], 0

    for para in paragraphs:
        p = para.strip()
        if not p:
            continue
        if _looks_like_heading(p):
            flush()
            title = re.sub(r"^#{1,6}\s*", "", p).strip().strip('"“”')
            continue
        if cur and cur_len + len(p) > _MAX_CHUNK_CHARS:
            flush()
        cur.append(p)
        cur_len += len(p) + 2

    flush()
    return chunks


def _read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown", ".txt", ".text"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            return "\n\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception:
            return ""
    return ""


# ---------------------------------------------------------------------------
# BM25 index
# ---------------------------------------------------------------------------

@dataclass
class _Index:
    chunks: list[dict] = field(default_factory=list)
    docs_tokens: list[list[str]] = field(default_factory=list)
    idf: dict = field(default_factory=dict)
    avgdl: float = 0.0
    sources: list[str] = field(default_factory=list)


_index: Optional[_Index] = None


def build_index() -> _Index:
    """Read the corpus folder, chunk every document, and build the BM25 index."""
    folder = _knowledge_dir()
    chunks: list[dict] = []
    sources: list[str] = []

    if folder.exists():
        for path in sorted(folder.glob("**/*")):
            if not path.is_file():
                continue
            if path.name.startswith((".", "_")):
                continue
            if path.suffix.lower() not in _READABLE_SUFFIXES:
                continue
            text = _read_file(path)
            if text.strip():
                sources.append(path.name)
                chunks.extend(chunk_document(path.name, text))

    idx = _Index(chunks=chunks, sources=sources)
    idx.docs_tokens = [_tokenize(c["title"] + " \n " + c["text"]) for c in chunks]

    df: dict[str, int] = {}
    for toks in idx.docs_tokens:
        for term in set(toks):
            df[term] = df.get(term, 0) + 1

    n_docs = max(1, len(chunks))
    idx.idf = {
        term: math.log(1 + (n_docs - n + 0.5) / (n + 0.5)) for term, n in df.items()
    }
    idx.avgdl = (sum(len(t) for t in idx.docs_tokens) / n_docs) if chunks else 0.0
    return idx


def get_index() -> _Index:
    global _index
    if _index is None:
        _index = build_index()
    return _index


def reindex() -> dict:
    """Rebuild the index from disk (e.g. after dropping new files)."""
    global _index
    _index = build_index()
    return corpus_stats()


def corpus_stats() -> dict:
    idx = get_index()
    return {
        "files": idx.sources,
        "file_count": len(idx.sources),
        "chunk_count": len(idx.chunks),
    }


def search(query: str, k: int = 5) -> list[dict]:
    """Return the top-``k`` chunks for ``query`` by BM25 score (desc).

    Each result is ``{source, section, text, score}``. Returns ``[]`` when the
    corpus is empty or nothing matches.
    """
    idx = get_index()
    if not idx.chunks:
        return []
    q_terms = _tokenize(query)
    if not q_terms:
        return []

    avgdl = idx.avgdl or 1.0
    scores: list[float] = []
    for toks in idx.docs_tokens:
        if not toks:
            scores.append(0.0)
            continue
        tf: dict[str, int] = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        dl = len(toks)
        s = 0.0
        for t in q_terms:
            f = tf.get(t)
            if not f:
                continue
            idf = idx.idf.get(t, 0.0)
            s += idf * (f * (_K1 + 1)) / (f + _K1 * (1 - _B + _B * dl / avgdl))
        scores.append(s)

    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    out: list[dict] = []
    for i in ranked[:k]:
        if scores[i] <= 0:
            break
        c = idx.chunks[i]
        out.append(
            {
                "source": c["source"],
                "section": c["title"],
                "text": c["text"],
                "score": round(scores[i], 3),
            }
        )
    return out
