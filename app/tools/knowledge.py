"""``search_knowledge`` tool — retrieve relevant reference passages.

Thin wrapper over :mod:`app.retrieval`. The model calls this with a focused
query when it needs BluChip program / policy / T&C / FAQ information; it returns
the most relevant chunks (with their source + section) so the model can answer
from real text instead of memory.
"""

from __future__ import annotations

from typing import Any

from .. import retrieval
from ..config import settings


async def search_knowledge(tool_input: dict, session: Any) -> dict:
    """Search the knowledge base and return the top matching passages.

    Input: ``{"query": "<focused search terms>"}``.
    Returns: ``{"query", "count", "results": [{source, section, text}], ...}``.
    Returns an empty result set (never fabricated content) when nothing matches.
    """
    query = str(tool_input.get("query", "") or "").strip()
    if not query:
        return {"query": "", "count": 0, "results": [], "message": "Empty query."}

    k = settings.RETRIEVAL_TOP_K
    results = retrieval.search(query, k)

    if not results:
        return {
            "query": query,
            "count": 0,
            "results": [],
            "message": (
                "No matching information found in the knowledge base. Tell the "
                "agent you don't have that information rather than guessing."
            ),
        }

    return {
        "query": query,
        "count": len(results),
        "results": [
            {"source": r["source"], "section": r["section"], "text": r["text"]}
            for r in results
        ],
    }
