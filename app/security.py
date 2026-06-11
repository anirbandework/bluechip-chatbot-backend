"""Password hashing, JWT access tokens, and one-time (invite/reset/refresh) tokens."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings


def hash_password(password: str) -> str:
    # bcrypt operates on <=72 bytes; truncate consistently (also done in verify).
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---- JWT access tokens ----

def create_access_token(user_id: str) -> str:
    now = _now()
    payload = {
        "sub": user_id,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES)).timestamp()
        ),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode/validate a JWT; raises jwt exceptions on invalid/expired tokens."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.JWT_ALGORITHM])


# ---- opaque one-time tokens (invite / reset / refresh) ----

def hash_token(raw: str) -> str:
    """SHA-256 of a raw token — only this hash is stored server-side."""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def new_opaque_token() -> tuple[str, str]:
    """Return (raw_token_to_send, token_hash_to_store)."""
    raw = secrets.token_urlsafe(32)
    return raw, hash_token(raw)
