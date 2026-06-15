"""Chat persistence service.

Bridges the providers' transient :class:`~app.sessions.Session` (transcript /
state / events) to the database: a chat is loaded into a Session, the provider
runs against it untouched, then the turn is persisted back. Keeps the LLM
provider/tool code unaware of the database.
"""

from __future__ import annotations

import uuid
from datetime import timedelta

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
    """Build a transient Session from a chat's stored messages + state.

    Messages folded into the compaction ``summary`` are excluded from the
    transcript (only the recent ones after ``summary_msg_count`` are kept); the
    summary is injected into the model context instead, so nothing is forgotten.
    The full message set always remains in the DB for the chat view.
    """
    msgs = (
        await db.execute(
            select(dbm.Message)
            .where(dbm.Message.chat_id == chat.id)
            .order_by(dbm.Message.created_at, dbm.Message.id)
        )
    ).scalars().all()
    st = chat.state if isinstance(chat.state, dict) else {}
    summary = str(st.get("summary", "") or "")
    boundary = max(0, min(int(st.get("summary_msg_count", 0) or 0), len(msgs)))
    recent = msgs[boundary:]
    sess = Session(
        id=str(chat.id),
        transcript=[{"role": m.role, "text": m.content} for m in recent],
    )
    sess.state = (
        SessionState(**st["state"]) if st.get("state") else default_session_state()
    )
    sess.events = list(st.get("events", []))
    sess.draft_fields = dict(st.get("draft_fields") or {})
    sess.summary = summary
    sess.summary_msg_count = boundary
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
    # Stamp the new rows with strictly increasing created_at so a turn's user and
    # assistant rows never share a timestamp (ties would make ordering — and thus
    # the compaction boundary — non-deterministic).
    base = utcnow()
    for offset, turn in enumerate(session.transcript[prior_len:]):
        db.add(
            dbm.Message(
                chat_id=chat.id,
                role=turn.get("role", "assistant"),
                content=turn.get("text", ""),
                created_at=base + timedelta(microseconds=offset),
            )
        )

    # Preserve a more-compacted summary if a concurrent compaction advanced the
    # boundary while this turn was streaming (this overwrites the whole JSON blob,
    # so re-read it and keep the furthest boundary to avoid a lost update).
    existing = chat.state if isinstance(chat.state, dict) else {}
    committed_boundary = int(existing.get("summary_msg_count", 0) or 0)
    if committed_boundary > session.summary_msg_count:
        summary, summary_boundary = str(existing.get("summary", "") or ""), committed_boundary
    else:
        summary, summary_boundary = session.summary, session.summary_msg_count

    chat.state = {
        "state": session.state.model_dump(mode="json"),
        "events": session.events,
        "draft_fields": session.draft_fields,
        "summary": summary,
        "summary_msg_count": summary_boundary,
    }
    chat.provider = provider
    if chat.title in ("", "New chat"):
        for turn in session.transcript:
            if turn.get("role") == "user" and turn.get("text"):
                chat.title = title_from(turn["text"])
                break
    chat.updated_at = utcnow()


async def compact_session(
    db: AsyncSession,
    chat: dbm.Chat,
    session: Session,
    provider,
    *,
    keep_recent: int,
) -> int:
    """Fold all but the most recent ``keep_recent`` transcript turns into the
    running summary, in place on ``session`` and ``chat.state``.

    The folded messages stay in the DB (the chat view is unchanged); only the
    model's context shrinks. Returns the number of turns folded (0 ONLY when
    there was nothing to compact). Raises if summarization fails/truncates — the
    boundary must not advance on a bad summary, or the model would lose the tail.
    Does not commit — the caller does.
    """
    transcript = session.transcript
    fold_count = len(transcript) - max(0, keep_recent)
    if fold_count <= 0:
        return 0

    to_fold = transcript[:fold_count]
    convo = "\n".join(
        f"{'Agent' if t.get('role') == 'user' else 'Assistant'}: {t.get('text', '')}"
        for t in to_fold
    )
    prompt = (
        (f"Summary so far:\n{session.summary}\n\n" if session.summary else "")
        + "Conversation to fold into the summary:\n"
        + convo
    )

    new_summary = (await provider.summarize(prompt)).strip()
    if not new_summary:
        # Empty or truncated (providers return "" on a max_tokens cut-off). Do NOT
        # advance the boundary — leaving the chat uncompacted is the safe failure.
        raise RuntimeError("Summarization produced no usable summary.")

    session.summary = new_summary
    session.summary_msg_count += fold_count
    session.transcript = transcript[fold_count:]

    # Persist the compaction immediately so it survives even if a later step
    # fails (merge into the existing JSON state rather than overwriting it).
    new_state = dict(chat.state or {})
    new_state["summary"] = session.summary
    new_state["summary_msg_count"] = session.summary_msg_count
    chat.state = new_state
    chat.updated_at = utcnow()
    return fold_count
