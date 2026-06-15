"""Chat endpoints: streaming /api/chat (persisted, auth-gated) + chat CRUD."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from .. import db_models as dbm
from ..config import settings
from ..db import SessionLocal, get_session
from ..deps import has_permission, require_permission
from ..models import ChatRequest
from ..redact import CodeRedactor, scrub_codes
from ..providers import default_provider_id, get_provider
from ..schemas import (
    ChatDetail,
    ChatMessageOut,
    ChatOwnerStat,
    ChatSummary,
    CompactResult,
    OwnerBrief,
    RenameChatRequest,
)
from ..services.chats import (
    compact_session,
    get_or_create_chat,
    load_session,
    persist_turn,
)

router = APIRouter(tags=["chats"])


# --------------------------------------------------------------------------- #
# Streaming chat (one assistant turn) — persists the conversation.
# --------------------------------------------------------------------------- #

@router.post("/api/chat")
async def chat(
    req: ChatRequest,
    user: dbm.User = Depends(require_permission("chats.use")),
    db: AsyncSession = Depends(get_session),
):
    provider_id = req.provider or default_provider_id()
    provider = get_provider(provider_id)

    chat_obj = await get_or_create_chat(
        db, user_id=user.id, chat_id=req.session_id, provider=provider_id
    )
    await db.commit()  # persist the (possibly new) chat so its id is durable
    session = await load_session(db, chat_obj)
    # Values submitted from a "complete the draft" card — accumulate them on the
    # session so render_email_template always has them (the model can't drop one).
    if req.form_fields:
        session.draft_fields.update(
            {
                str(k): str(v)
                for k, v in req.form_fields.items()
                if v is not None and str(v) != ""
            }
        )
    # Auto-compact once the (uncompacted) transcript gets long, so a never-ending
    # chat can't overflow the context window. Best-effort: on any failure we just
    # proceed with the full transcript. The full messages stay in the DB.
    if (
        settings.COMPACT_AFTER_MESSAGES
        and provider is not None
        and provider.available()
        and len(session.transcript) > settings.COMPACT_AFTER_MESSAGES
    ):
        try:
            folded = await compact_session(
                db, chat_obj, session, provider,
                keep_recent=settings.COMPACT_KEEP_RECENT,
            )
            if folded:
                await db.commit()
        except Exception:  # noqa: BLE001 — compaction must never break a turn
            await db.rollback()
            session = await load_session(db, chat_obj)
    prior_len = len(session.transcript)
    chat_uuid = chat_obj.id
    chat_id = str(chat_uuid)
    message = req.message

    async def event_stream():
        yield {"event": "session", "data": json.dumps({"session_id": chat_id})}
        redactor = CodeRedactor()  # strip internal template codes (T1–T10) from agent-facing text
        try:
            if provider is None:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": f"Unknown provider: {provider_id!r}"}),
                }
            elif not provider.available():
                yield {
                    "event": "error",
                    "data": json.dumps(
                        {"message": f"Provider '{provider_id}' is not configured (missing API key)."}
                    ),
                }
            else:
                async for event in provider.stream_turn(session, message):
                    if event["event"] == "token":
                        clean = redactor.feed(event["data"].get("text", ""))
                        if clean:
                            yield {"event": "token", "data": json.dumps({"text": clean})}
                    else:
                        yield {"event": event["event"], "data": json.dumps(event["data"])}
                tail = redactor.flush()
                if tail:
                    yield {"event": "token", "data": json.dumps({"text": tail})}
                # Scrub the same codes from what gets persisted (so reloaded chats
                # match what was shown).
                for turn in session.transcript[prior_len:]:
                    if turn.get("role") == "assistant" and turn.get("text"):
                        turn["text"] = scrub_codes(turn["text"])
                # Persist the turn with a fresh session (the request session may
                # be closed by the time the stream finishes).
                async with SessionLocal() as wdb:
                    wchat = await wdb.get(dbm.Chat, chat_uuid)
                    if wchat is not None:
                        await persist_turn(
                            wdb, wchat, session, provider=provider_id, prior_len=prior_len
                        )
                        await wdb.commit()
        except Exception as exc:  # noqa: BLE001 — surface any failure to the client
            yield {"event": "error", "data": json.dumps({"message": str(exc)})}
        finally:
            yield {"event": "done", "data": json.dumps({"session_id": chat_id})}

    return EventSourceResponse(event_stream())


# --------------------------------------------------------------------------- #
# Chat history CRUD
# --------------------------------------------------------------------------- #

async def _own_chat(db: AsyncSession, user: dbm.User, chat_id: uuid.UUID) -> dbm.Chat:
    chat = await db.get(dbm.Chat, chat_id)
    if chat is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat not found")
    if chat.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your chat")
    return chat


@router.get("/api/chats", response_model=list[ChatSummary])
async def list_chats(
    q: str | None = Query(None),
    all_users: bool = Query(False, alias="all"),
    user_id: uuid.UUID | None = Query(None, description="Oversight: view one user's chats"),
    user: dbm.User = Depends(require_permission("chats.use")),
    db: AsyncSession = Depends(get_session),
):
    can_oversee = has_permission(user, "chats.read_all")

    # Decide whose chats to return.
    if user_id is not None and user_id != user.id:
        # Viewing a specific other user's chats — oversight only.
        if not can_oversee:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        scope_user_id: uuid.UUID | None = user_id
        label_owner = True
    elif all_users and can_oversee:
        # Every user's chats, lumped together with owner labels.
        scope_user_id = None
        label_owner = True
    else:
        # Just my own chats.
        scope_user_id = user.id
        label_owner = False

    stmt = select(dbm.Chat)
    if scope_user_id is not None:
        stmt = stmt.where(dbm.Chat.user_id == scope_user_id)
    if q:
        like = f"%{q.lower()}%"
        sub = select(dbm.Message.chat_id).where(func.lower(dbm.Message.content).like(like))
        stmt = stmt.where(
            or_(func.lower(dbm.Chat.title).like(like), dbm.Chat.id.in_(sub))
        )
    chats = (
        await db.execute(stmt.order_by(dbm.Chat.updated_at.desc()))
    ).scalars().all()
    if not chats:
        return []

    ids = [c.id for c in chats]
    counts = dict(
        (
            await db.execute(
                select(dbm.Message.chat_id, func.count())
                .where(dbm.Message.chat_id.in_(ids))
                .group_by(dbm.Message.chat_id)
            )
        ).all()
    )
    owners: dict[uuid.UUID, dbm.User] = {}
    if label_owner:
        owner_ids = {c.user_id for c in chats}
        owners = {
            u.id: u
            for u in (
                await db.execute(select(dbm.User).where(dbm.User.id.in_(owner_ids)))
            ).scalars().all()
        }
    return [
        ChatSummary(
            id=c.id,
            title=c.title,
            provider=c.provider,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=counts.get(c.id, 0),
            owner=(
                OwnerBrief(id=c.user_id, email=owners[c.user_id].email)
                if label_owner and c.user_id in owners
                else None
            ),
        )
        for c in chats
    ]


@router.get("/api/chats/owners", response_model=list[ChatOwnerStat])
async def list_chat_owners(
    user: dbm.User = Depends(require_permission("chats.read_all")),
    db: AsyncSession = Depends(get_session),
):
    """Users who own at least one chat — the picker for chat oversight."""
    counts = dict(
        (
            await db.execute(
                select(dbm.Chat.user_id, func.count()).group_by(dbm.Chat.user_id)
            )
        ).all()
    )
    if not counts:
        return []
    owners = (
        await db.execute(select(dbm.User).where(dbm.User.id.in_(counts.keys())))
    ).scalars().all()
    return sorted(
        (
            ChatOwnerStat(
                id=u.id,
                email=u.email,
                full_name=u.full_name or "",
                chat_count=counts.get(u.id, 0),
            )
            for u in owners
        ),
        key=lambda o: (o.full_name or o.email).lower(),
    )


@router.get("/api/chats/{chat_id}", response_model=ChatDetail)
async def get_chat(
    chat_id: uuid.UUID,
    user: dbm.User = Depends(require_permission("chats.use")),
    db: AsyncSession = Depends(get_session),
):
    chat = await db.get(dbm.Chat, chat_id)
    if chat is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat not found")
    if chat.user_id != user.id and not has_permission(user, "chats.read_all"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your chat")

    msgs = (
        await db.execute(
            select(dbm.Message)
            .where(dbm.Message.chat_id == chat.id)
            .order_by(dbm.Message.created_at, dbm.Message.id)
        )
    ).scalars().all()
    state = (chat.state or {}).get("state", {}) if isinstance(chat.state, dict) else {}
    owner = None
    if chat.user_id != user.id:
        ou = await db.get(dbm.User, chat.user_id)
        owner = OwnerBrief(id=chat.user_id, email=ou.email) if ou else None
    return ChatDetail(
        id=chat.id,
        title=chat.title,
        provider=chat.provider,
        state=state,
        messages=[
            ChatMessageOut(role=m.role, content=m.content, created_at=m.created_at)
            for m in msgs
        ],
        owner=owner,
    )


@router.post("/api/chats/{chat_id}/compact", response_model=CompactResult)
async def compact_chat(
    chat_id: uuid.UUID,
    user: dbm.User = Depends(require_permission("chats.use")),
    db: AsyncSession = Depends(get_session),
):
    """Manually compact a chat: fold older messages into a summary now.

    The full messages stay in the DB and the chat view; only the model's context
    is condensed (the summary is injected so nothing is forgotten).
    """
    chat = await _own_chat(db, user, chat_id)
    total = (
        await db.execute(
            select(func.count()).select_from(dbm.Message).where(dbm.Message.chat_id == chat.id)
        )
    ).scalar_one()

    provider_id = chat.provider or default_provider_id()
    provider = get_provider(provider_id)
    if provider is None or not provider.available():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Provider '{provider_id}' is not available to summarize this chat.",
        )

    session = await load_session(db, chat)
    try:
        folded = await compact_session(
            db, chat, session, provider, keep_recent=settings.COMPACT_KEEP_RECENT
        )
    except Exception as exc:  # noqa: BLE001
        await db.rollback()
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, f"Could not summarize the chat: {exc}"
        ) from exc
    if folded:
        await db.commit()

    return CompactResult(
        folded=folded,
        kept=len(session.transcript),
        total_messages=total,
        has_summary=bool(session.summary),
    )


@router.patch("/api/chats/{chat_id}", response_model=ChatSummary)
async def rename_chat(
    chat_id: uuid.UUID,
    body: RenameChatRequest,
    user: dbm.User = Depends(require_permission("chats.use")),
    db: AsyncSession = Depends(get_session),
):
    chat = await _own_chat(db, user, chat_id)
    chat.title = body.title.strip() or chat.title
    await db.commit()
    count = (
        await db.execute(
            select(func.count()).select_from(dbm.Message).where(dbm.Message.chat_id == chat.id)
        )
    ).scalar_one()
    return ChatSummary(
        id=chat.id,
        title=chat.title,
        provider=chat.provider,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        message_count=count,
    )


@router.delete("/api/chats/{chat_id}")
async def delete_chat(
    chat_id: uuid.UUID,
    user: dbm.User = Depends(require_permission("chats.use")),
    db: AsyncSession = Depends(get_session),
):
    chat = await _own_chat(db, user, chat_id)
    await db.delete(chat)
    await db.commit()
    return {"ok": True}
