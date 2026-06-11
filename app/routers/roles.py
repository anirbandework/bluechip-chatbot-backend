"""Dynamic role management: list permissions, CRUD roles."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import audit
from .. import db_models as dbm
from ..db import get_session
from ..deps import client_ip, require_permission
from ..permissions import PERMISSIONS
from ..schemas import (
    CreateRoleRequest,
    PermissionOut,
    RoleOut,
    UpdateRoleRequest,
    role_out,
)

router = APIRouter(prefix="/api/roles", tags=["roles"])


def _validate_perms(perms: list[str]) -> list[str]:
    unknown = [p for p in perms if p not in PERMISSIONS]
    if unknown:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"Unknown permission(s): {', '.join(unknown)}"
        )
    seen: set[str] = set()
    out: list[str] = []
    for p in perms:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


async def _user_count(db: AsyncSession, role_id: uuid.UUID) -> int:
    return (
        await db.execute(
            select(func.count()).select_from(dbm.User).where(dbm.User.role_id == role_id)
        )
    ).scalar_one()


@router.get("/permissions", response_model=list[PermissionOut])
async def list_permissions(_: dbm.User = Depends(require_permission("roles.read"))):
    return [PermissionOut(key=k, label=v) for k, v in PERMISSIONS.items()]


@router.get("", response_model=list[RoleOut])
async def list_roles(
    _: dbm.User = Depends(require_permission("roles.read")),
    db: AsyncSession = Depends(get_session),
):
    roles = (await db.execute(select(dbm.Role).order_by(dbm.Role.name))).scalars().all()
    counts = dict(
        (
            await db.execute(
                select(dbm.User.role_id, func.count()).group_by(dbm.User.role_id)
            )
        ).all()
    )
    return [role_out(r, counts.get(r.id, 0)) for r in roles]


@router.post("", response_model=RoleOut, status_code=201)
async def create_role(
    body: CreateRoleRequest,
    request: Request,
    actor: dbm.User = Depends(require_permission("roles.manage")),
    db: AsyncSession = Depends(get_session),
):
    name = body.name.strip()
    if (
        await db.execute(select(dbm.Role).where(dbm.Role.name == name))
    ).scalar_one_or_none() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "A role with that name already exists")
    role = dbm.Role(
        name=name,
        description=body.description.strip(),
        permissions=_validate_perms(body.permissions),
        is_system=False,
    )
    db.add(role)
    await audit.record(
        db, actor=actor, action="role.created", target_type="role",
        detail={"name": name}, ip=client_ip(request),
    )
    await db.commit()
    await db.refresh(role)
    return role_out(role, 0)


@router.patch("/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: uuid.UUID,
    body: UpdateRoleRequest,
    request: Request,
    actor: dbm.User = Depends(require_permission("roles.manage")),
    db: AsyncSession = Depends(get_session),
):
    role = await db.get(dbm.Role, role_id)
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    fields = body.model_fields_set
    if "name" in fields and body.name:
        clash = (
            await db.execute(
                select(dbm.Role).where(
                    dbm.Role.name == body.name.strip(), dbm.Role.id != role.id
                )
            )
        ).scalar_one_or_none()
        if clash is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "A role with that name already exists")
        role.name = body.name.strip()
    if "description" in fields and body.description is not None:
        role.description = body.description.strip()
    if "permissions" in fields and body.permissions is not None:
        role.permissions = _validate_perms(body.permissions)
    await audit.record(
        db, actor=actor, action="role.updated", target_type="role",
        target_id=str(role.id), detail={"name": role.name}, ip=client_ip(request),
    )
    await db.commit()
    await db.refresh(role)
    return role_out(role, await _user_count(db, role.id))


@router.delete("/{role_id}")
async def delete_role(
    role_id: uuid.UUID,
    request: Request,
    actor: dbm.User = Depends(require_permission("roles.manage")),
    db: AsyncSession = Depends(get_session),
):
    role = await db.get(dbm.Role, role_id)
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    count = await _user_count(db, role.id)
    if count > 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Cannot delete a role assigned to {count} user(s) — reassign them first",
        )
    await audit.record(
        db, actor=actor, action="role.deleted", target_type="role",
        target_id=str(role.id), detail={"name": role.name}, ip=client_ip(request),
    )
    await db.delete(role)
    await db.commit()
    return {"ok": True}
