"""First-boot seeding: default roles + bootstrap SuperAdmin (idempotent)."""

from __future__ import annotations

import logging

from sqlalchemy import func, select

from . import db_models as dbm
from .config import settings
from .db import SessionLocal
from .permissions import DEFAULT_ROLES
from .security import hash_password

log = logging.getLogger("bluchip.seed")


async def seed() -> None:
    async with SessionLocal() as db:
        # --- default roles (created once; left editable afterwards) ---
        existing = {
            r.name for r in (await db.execute(select(dbm.Role))).scalars().all()
        }
        for spec in DEFAULT_ROLES:
            if spec["name"] not in existing:
                db.add(
                    dbm.Role(
                        name=spec["name"],
                        description=spec["description"],
                        permissions=spec["permissions"],
                        is_system=True,
                    )
                )
        await db.commit()

        # --- bootstrap SuperAdmin ---
        email = settings.SUPERADMIN_EMAIL.strip().lower()
        if email:
            found = (
                await db.execute(select(dbm.User).where(dbm.User.email == email))
            ).scalar_one_or_none()
            if found is None:
                if not settings.SUPERADMIN_PASSWORD:
                    log.warning(
                        "SUPERADMIN_EMAIL set but SUPERADMIN_PASSWORD empty — "
                        "skipping SuperAdmin bootstrap."
                    )
                else:
                    db.add(
                        dbm.User(
                            email=email,
                            full_name=settings.SUPERADMIN_NAME,
                            hashed_password=hash_password(settings.SUPERADMIN_PASSWORD),
                            is_superadmin=True,
                            is_active=True,
                        )
                    )
                    await db.commit()
                    log.info("Bootstrapped SuperAdmin %s", email)
        else:
            count = (
                await db.execute(select(func.count()).select_from(dbm.User))
            ).scalar_one()
            if count == 0:
                log.warning(
                    "No users exist and SUPERADMIN_EMAIL is unset — set "
                    "SUPERADMIN_EMAIL / SUPERADMIN_PASSWORD to create the first admin."
                )
