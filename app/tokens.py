"""Helpers to issue access/refresh tokens and invite/reset links."""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from . import db_models as dbm
from .config import settings
from .db_models import utcnow
from .security import create_access_token, new_opaque_token


async def issue_tokens(db: AsyncSession, user: dbm.User) -> tuple[str, str]:
    """Create a JWT access token and a tracked opaque refresh token."""
    access = create_access_token(str(user.id))
    raw, token_hash = new_opaque_token()
    db.add(
        dbm.RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=utcnow() + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS),
        )
    )
    return access, raw


async def create_link_token(db: AsyncSession, user: dbm.User, purpose: str) -> str:
    """Create a one-time invite/reset token; return the raw token (store the hash)."""
    raw, token_hash = new_opaque_token()
    hours = (
        settings.INVITE_TOKEN_TTL_HOURS
        if purpose == "invite"
        else settings.RESET_TOKEN_TTL_HOURS
    )
    db.add(
        dbm.AuthToken(
            user_id=user.id,
            token_hash=token_hash,
            purpose=purpose,
            expires_at=utcnow() + timedelta(hours=hours),
        )
    )
    return raw


def build_link(purpose: str, token: str) -> str:
    base = settings.FRONTEND_URL.rstrip("/")
    path = "/accept-invite" if purpose == "invite" else "/reset-password"
    return f"{base}{path}?token={token}"
