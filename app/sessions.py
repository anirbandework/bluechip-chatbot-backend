"""In-memory conversation store (CONTRACTS §5).

Holds a per-session ``Session`` keyed by id. A ``Session`` carries a
**provider-neutral** conversation ``transcript`` (so either LLM provider can
rebuild its own native history and the user can even switch providers
mid-conversation), the decision ``SessionState`` shown in the frontend panel,
and an audit ``events`` log appended by the ``record_outcome`` tool.

The store is a simple process-local dict — fine for the MVP. There is no
persistence and no network access at import time.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .models import SessionState, default_session_state


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Session:
    """A single agent-assist conversation.

    Attributes:
        id: Stable session identifier (UUID).
        transcript: Provider-neutral turn list — ``[{"role": "user"|"assistant",
            "text": str}, ...]``. Each provider converts this to its own native
            message format at the start of a turn; the deterministic workflow
            memory lives in ``state``/``events``, not in the transcript.
        state: The decision-panel state mirrored to the frontend (§5).
        events: Audit log appended by ``record_outcome``.
    """

    id: str
    transcript: list[dict] = field(default_factory=list)
    state: SessionState = field(default_factory=default_session_state)
    events: list[dict] = field(default_factory=list)
    created_at: str = field(default_factory=_now_iso)

    def title(self) -> str:
        """A short title derived from the first user message."""
        for turn in self.transcript:
            if turn.get("role") == "user" and turn.get("text"):
                text = " ".join(turn["text"].split())
                return text[:48] + "…" if len(text) > 48 else text
        return "New conversation"


class SessionStore:
    """Process-local, in-memory map of session_id -> Session."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> Session:
        """Return the existing session, or create a fresh one.

        A new UUID id is generated when ``session_id`` is ``None`` or unknown.
        """
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        new_id = session_id or str(uuid.uuid4())
        session = Session(id=new_id)
        self._sessions[new_id] = session
        return session

    def get(self, session_id: str) -> Optional[Session]:
        """Return an existing session, or None."""
        return self._sessions.get(session_id)

    def list(self) -> list[Session]:
        """Non-empty sessions, newest first (for the history sidebar)."""
        sessions = [s for s in self._sessions.values() if s.transcript]
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)


# Module-level singleton used by the chat endpoint.
store = SessionStore()
