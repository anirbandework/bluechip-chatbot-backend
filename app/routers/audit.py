"""Read-only audit log (requires the audit.read permission)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import db_models as dbm
from ..db import get_session
from ..deps import require_permission
from ..schemas import AuditOut

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=list[AuditOut])
async def list_audit(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _: dbm.User = Depends(require_permission("audit.read")),
    db: AsyncSession = Depends(get_session),
):
    rows = (
        await db.execute(
            select(dbm.AuditLog)
            .order_by(dbm.AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    return [
        AuditOut(
            id=r.id,
            actor_email=r.actor_email,
            action=r.action,
            target_type=r.target_type,
            target_id=r.target_id,
            detail=r.detail,
            ip=r.ip,
            created_at=r.created_at,
        )
        for r in rows
    ]
