"""FastAPI auth dependencies: current user + permission / superadmin guards."""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from . import db_models as dbm
from .db import get_session
from .security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_session),
) -> dbm.User:
    if creds is None or not creds.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = decode_access_token(creds.credentials)
        if payload.get("type") != "access":
            raise ValueError("wrong token type")
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    user = await db.get(dbm.User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Account not found or disabled")
    return user


def has_permission(user: dbm.User, perm: str) -> bool:
    if user.is_superadmin:
        return True
    return perm in (user.role.permissions or []) if user.role else False


def require_permission(*perms: str):
    """Dependency factory: require ALL listed permission keys (superadmin bypasses)."""

    async def _dep(user: dbm.User = Depends(get_current_user)) -> dbm.User:
        if not all(has_permission(user, p) for p in perms):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user

    return _dep


async def get_current_superadmin(
    user: dbm.User = Depends(get_current_user),
) -> dbm.User:
    if not user.is_superadmin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "SuperAdmin only")
    return user


def client_ip(request: Request) -> str | None:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else None
