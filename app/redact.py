"""Strip internal email-template codes (T1–T10) from agent-facing assistant text.

The model needs the codes as `render_email_template`'s `template_id`, so it tends
to echo them ("the name-mismatch denial (T7)") even when the prompt forbids it.
This is a deterministic, streaming-safe post-filter that removes the parenthesized
codes from both the streamed tokens and the persisted transcript. The model's
plain-English template names ("the name-mismatch denial email") are kept.
"""

from __future__ import annotations

import re

# A complete parenthesized template code, optionally with a leading space:
#   " (T7)", "(T10)".
_FULL = re.compile(r" ?\(T(?:10|[1-9])\)")

# A trailing fragment that might still grow into a complete code, so the streaming
# filter holds it back: a lone trailing space, or "(", "(T", "(T1", " (T10", …
_PARTIAL = re.compile(r"(?: ?\(T?\d{0,2}| )$")


def scrub_codes(text: str) -> str:
    """Remove complete `(Txx)` template codes from a finished string."""
    return _FULL.sub("", text)


class CodeRedactor:
    """Streaming filter: `feed()` text chunks, get back code-free chunks.

    Holds back a trailing fragment that could still complete into a code, so a
    pattern split across chunks (… "(T", then "7)" …) is never emitted whole.
    Call `flush()` at the end to release whatever is buffered.
    """

    def __init__(self) -> None:
        self._buf = ""

    def feed(self, chunk: str) -> str:
        self._buf = _FULL.sub("", self._buf + chunk)
        m = _PARTIAL.search(self._buf)
        if m:
            emit, self._buf = self._buf[: m.start()], self._buf[m.start() :]
        else:
            emit, self._buf = self._buf, ""
        return emit

    def flush(self) -> str:
        out = _FULL.sub("", self._buf)
        self._buf = ""
        return out
