"""Chat persistence service.

Bridges the providers' transient :class:`~app.sessions.Session` (transcript /
state / events) to the database: a chat is loaded into a Session, the provider
runs against it untouched, then the turn is persisted back. Keeps the LLM
provider/tool code unaware of the database.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import db_models as dbm
from ..db_models import utcnow
from ..models import SessionState, default_session_state
from ..sessions import Session


def title_from(text: str) -> str:
    t = " ".join((text or "").split())
    if not t:
        return "New chat"
    return (t[:48] + "…") if len(t) > 48 else t


def _coerce_uuid(value) -> uuid.UUID | None:
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        return None


async def get_or_create_chat(
    db: AsyncSession, *, user_id: uuid.UUID, chat_id, provider: str | None
) -> dbm.Chat:
    """Return the user's existing chat, or a fresh one owned by them."""
    cid = _coerce_uuid(chat_id) if chat_id else None
    if cid is not None:
        chat = await db.get(dbm.Chat, cid)
        if chat is not None and chat.user_id == user_id:
            return chat
    chat = dbm.Chat(user_id=user_id, title="New chat", provider=provider, state={})
    db.add(chat)
    await db.flush()
    return chat


async def load_session(db: AsyncSession, chat: dbm.Chat) -> Session:
    """Build a transient Session from a chat's stored messages + state."""
    msgs = (
        await db.execute(
            select(dbm.Message)
            .where(dbm.Message.chat_id == chat.id)
            .order_by(dbm.Message.created_at)
        )
    ).scalars().all()
    sess = Session(
        id=str(chat.id),
        transcript=[{"role": m.role, "text": m.content} for m in msgs],
    )
    st = chat.state if isinstance(chat.state, dict) else {}
    sess.state = (
        SessionState(**st["state"]) if st.get("state") else default_session_state()
    )
    sess.events = list(st.get("events", []))
    return sess


async def persist_turn(
    db: AsyncSession,
    chat: dbm.Chat,
    session: Session,
    *,
    provider: str | None,
    prior_len: int,
) -> None:
    """Persist the messages added during a turn plus the updated state/title."""
    for turn in session.transcript[prior_len:]:
        db.add(
            dbm.Message(
                chat_id=chat.id,
                role=turn.get("role", "assistant"),
                content=turn.get("text", ""),
            )
        )
    chat.state = {
        "state": session.state.model_dump(mode="json"),
        "events": session.events,
    }
    chat.provider = provider
    if chat.title in ("", "New chat"):
        for turn in session.transcript:
            if turn.get("role") == "user" and turn.get("text"):
                chat.title = title_from(turn["text"])
                break
    chat.updated_at = utcnow()
