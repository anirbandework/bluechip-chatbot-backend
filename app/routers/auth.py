"""Authentication: login, refresh, logout, me, invite-accept, forgot/reset/change password."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .. import audit
from .. import db_models as dbm
from ..db import get_session
from ..db_models import utcnow
from ..deps import client_ip, get_current_user
from ..email import send_reset
from ..schemas import (
    AcceptInviteRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
    user_out,
)
from ..security import hash_password, hash_token, verify_password
from ..tokens import build_link, create_link_token, issue_tokens

router = APIRouter(prefix="/api/auth", tags=["auth"])


async def _consume_token(
    db: AsyncSession, raw: str, purpose: str
) -> tuple[dbm.AuthToken, dbm.User]:
    row = (
        await db.execute(
            select(dbm.AuthToken).where(
                dbm.AuthToken.token_hash == hash_token(raw),
                dbm.AuthToken.purpose == purpose,
            )
        )
    ).scalar_one_or_none()
    if row is None or row.used_at is not None or row.expires_at < utcnow():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This link is invalid or has expired.")
    user = await db.get(dbm.User, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Account not available.")
    return row, user


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest, request: Request, db: AsyncSession = Depends(get_session)
):
    email = body.email.strip().lower()
    user = (
        await db.execute(select(dbm.User).where(dbm.User.email == email))
    ).scalar_one_or_none()
    if (
        user is None
        or not user.is_active
        or not verify_password(body.password, user.hashed_password)
    ):
        await audit.record(
            db, actor=None, action="login.failed",
            detail={"email": email}, ip=client_ip(request),
        )
        await db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    user.last_login_at = utcnow()
    access, refresh = await issue_tokens(db, user)
    await audit.record(db, actor=user, action="login", ip=client_ip(request))
    await db.commit()
    await db.refresh(user)
    return TokenResponse(access_token=access, refresh_token=refresh, user=user_out(user))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_session)):
    row = (
        await db.execute(
            select(dbm.RefreshToken).where(
                dbm.RefreshToken.token_hash == hash_token(body.refresh_token)
            )
        )
    ).scalar_one_or_none()
    if row is None or row.revoked or row.expires_at < utcnow():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")
    user = await db.get(dbm.User, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Account not available")

    row.revoked = True  # rotate
    access, new_refresh = await issue_tokens(db, user)
    await db.commit()
    await db.refresh(user)
    return TokenResponse(access_token=access, refresh_token=new_refresh, user=user_out(user))


@router.post("/logout")
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_session)):
    row = (
        await db.execute(
            select(dbm.RefreshToken).where(
                dbm.RefreshToken.token_hash == hash_token(body.refresh_token)
            )
        )
    ).scalar_one_or_none()
    if row is not None:
        row.revoked = True
        await db.commit()
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(user: dbm.User = Depends(get_current_user)):
    return user_out(user)


@router.post("/accept-invite", response_model=TokenResponse)
async def accept_invite(
    body: AcceptInviteRequest, request: Request, db: AsyncSession = Depends(get_session)
):
    row, user = await _consume_token(db, body.token, "invite")
    user.hashed_password = hash_password(body.password)
    if body.full_name and not user.full_name:
        user.full_name = body.full_name.strip()
    user.must_change_password = False
    user.last_login_at = utcnow()
    row.used_at = utcnow()
    access, refresh = await issue_tokens(db, user)
    await audit.record(db, actor=user, action="invite.accepted", ip=client_ip(request))
    await db.commit()
    await db.refresh(user)
    return TokenResponse(access_token=access, refresh_token=refresh, user=user_out(user))


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest, db: AsyncSession = Depends(get_session)
):
    email = body.email.strip().lower()
    user = (
        await db.execute(select(dbm.User).where(dbm.User.email == email))
    ).scalar_one_or_none()
    # Always return ok (don't reveal whether the account exists).
    if user is not None and user.is_active and user.hashed_password is not None:
        raw = await create_link_token(db, user, "reset")
        await db.commit()
        await send_reset(user.email, build_link("reset", raw))
    return {"ok": True}


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest, request: Request, db: AsyncSession = Depends(get_session)
):
    row, user = await _consume_token(db, body.token, "reset")
    user.hashed_password = hash_password(body.password)
    user.must_change_password = False
    row.used_at = utcnow()
    # Sign out everywhere on a password reset.
    await db.execute(
        update(dbm.RefreshToken)
        .where(dbm.RefreshToken.user_id == user.id)
        .values(revoked=True)
    )
    await audit.record(db, actor=user, action="password.reset", ip=client_ip(request))
    await db.commit()
    return {"ok": True}


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    user: dbm.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not verify_password(body.current_password, user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    user.hashed_password = hash_password(body.new_password)
    user.must_change_password = False
    await audit.record(db, actor=user, action="password.changed")
    await db.commit()
    return {"ok": True}
