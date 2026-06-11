"""User management: list / create (invite) / update / delete / reset-password."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import audit
from .. import db_models as dbm
from ..db import get_session
from ..deps import client_ip, require_permission
from ..email import send_invite, send_reset
from ..schemas import (
    CreateUserRequest,
    InviteResult,
    ResetResult,
    UpdateUserRequest,
    UserOut,
    user_out,
)
from ..tokens import build_link, create_link_token

router = APIRouter(prefix="/api/users", tags=["users"])


async def _get_or_404(db: AsyncSession, user_id: uuid.UUID) -> dbm.User:
    user = await db.get(dbm.User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


async def _active_superadmins(db: AsyncSession) -> int:
    return (
        await db.execute(
            select(func.count())
            .select_from(dbm.User)
            .where(dbm.User.is_superadmin.is_(True), dbm.User.is_active.is_(True))
        )
    ).scalar_one()


@router.get("", response_model=list[UserOut])
async def list_users(
    _: dbm.User = Depends(require_permission("users.read")),
    db: AsyncSession = Depends(get_session),
):
    rows = (
        await db.execute(select(dbm.User).order_by(dbm.User.created_at))
    ).scalars().all()
    return [user_out(u) for u in rows]


@router.post("", response_model=InviteResult, status_code=201)
async def create_user(
    body: CreateUserRequest,
    request: Request,
    actor: dbm.User = Depends(require_permission("users.create")),
    db: AsyncSession = Depends(get_session),
):
    email = body.email.strip().lower()
    if (
        await db.execute(select(dbm.User).where(dbm.User.email == email))
    ).scalar_one_or_none() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "A user with that email already exists")

    if body.is_superadmin and not actor.is_superadmin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only a SuperAdmin can create a SuperAdmin")

    role = None
    if not body.is_superadmin and body.role_id is not None:
        role = await db.get(dbm.Role, body.role_id)
        if role is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown role")

    user = dbm.User(
        email=email,
        full_name=body.full_name.strip(),
        role_id=None if body.is_superadmin else body.role_id,
        is_superadmin=body.is_superadmin,
        is_active=True,
    )
    db.add(user)
    await db.flush()  # assign user.id
    raw = await create_link_token(db, user, "invite")
    await audit.record(
        db, actor=actor, action="user.created", target_type="user",
        target_id=str(user.id),
        detail={
            "email": email,
            "role": role.name if role else None,
            "is_superadmin": body.is_superadmin,
        },
        ip=client_ip(request),
    )
    await db.commit()
    await db.refresh(user)

    link = build_link("invite", raw)
    sent = await send_invite(user.email, user.full_name, link)
    return InviteResult(user=user_out(user), invite_link=link, email_sent=sent)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: uuid.UUID,
    body: UpdateUserRequest,
    request: Request,
    actor: dbm.User = Depends(require_permission("users.update")),
    db: AsyncSession = Depends(get_session),
):
    user = await _get_or_404(db, user_id)
    if user.is_superadmin and not actor.is_superadmin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only a SuperAdmin can edit a SuperAdmin")

    fields = body.model_fields_set
    if "is_superadmin" in fields and body.is_superadmin is not None:
        if not actor.is_superadmin:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "Only a SuperAdmin can change SuperAdmin status"
            )
        if (
            body.is_superadmin is False
            and user.is_superadmin
            and await _active_superadmins(db) <= 1
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot demote the last SuperAdmin")
        user.is_superadmin = body.is_superadmin
        if body.is_superadmin:
            user.role_id = None  # superadmins don't use a role
    if "full_name" in fields and body.full_name is not None:
        user.full_name = body.full_name.strip()
    if "role_id" in fields and not user.is_superadmin:
        if body.role_id is not None and await db.get(dbm.Role, body.role_id) is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown role")
        user.role_id = body.role_id
    if "is_active" in fields and body.is_active is not None:
        if user.id == actor.id and body.is_active is False:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You can't disable your own account")
        if (
            user.is_superadmin
            and body.is_active is False
            and await _active_superadmins(db) <= 1
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot disable the last SuperAdmin")
        user.is_active = body.is_active

    await audit.record(
        db, actor=actor, action="user.updated", target_type="user",
        target_id=str(user.id), detail={"fields": sorted(fields)}, ip=client_ip(request),
    )
    await db.commit()
    await db.refresh(user)
    return user_out(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    request: Request,
    actor: dbm.User = Depends(require_permission("users.delete")),
    db: AsyncSession = Depends(get_session),
):
    user = await _get_or_404(db, user_id)
    if user.id == actor.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You can't delete your own account")
    if user.is_superadmin:
        if not actor.is_superadmin:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only a SuperAdmin can delete a SuperAdmin")
        if await _active_superadmins(db) <= 1:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot delete the last SuperAdmin")
    await audit.record(
        db, actor=actor, action="user.deleted", target_type="user",
        target_id=str(user.id), detail={"email": user.email}, ip=client_ip(request),
    )
    await db.delete(user)
    await db.commit()
    return {"ok": True}


@router.post("/{user_id}/reset-password", response_model=ResetResult)
async def admin_reset_password(
    user_id: uuid.UUID,
    request: Request,
    actor: dbm.User = Depends(require_permission("users.update")),
    db: AsyncSession = Depends(get_session),
):
    """Re-issue an invite (if still pending) or a password-reset link."""
    user = await _get_or_404(db, user_id)
    purpose = "invite" if user.hashed_password is None else "reset"
    raw = await create_link_token(db, user, purpose)
    await audit.record(
        db, actor=actor, action="user.reset_password", target_type="user",
        target_id=str(user.id), detail={"email": user.email, "purpose": purpose},
        ip=client_ip(request),
    )
    await db.commit()

    link = build_link(purpose, raw)
    if purpose == "invite":
        sent = await send_invite(user.email, user.full_name, link)
    else:
        sent = await send_reset(user.email, link)
    return ResetResult(reset_link=link, email_sent=sent)
