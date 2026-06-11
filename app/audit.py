"""Audit-log helper. ``record()`` stages an entry; the caller commits."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from . import db_models as dbm


async def record(
    db: AsyncSession,
    *,
    actor: "dbm.User | None",
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    detail: dict | None = None,
    ip: str | None = None,
) -> None:
    db.add(
        dbm.AuditLog(
            actor_user_id=actor.id if actor else None,
            actor_email=actor.email if actor else "",
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail or {},
            ip=ip,
        )
    )
