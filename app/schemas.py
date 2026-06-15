"""Pydantic request/response DTOs for the auth + admin + chat APIs."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from . import db_models as dbm
from .permissions import ALL_PERMISSIONS


def effective_permissions(user: "dbm.User") -> list[str]:
    """The permission keys this user effectively has."""
    if user.is_superadmin:
        return list(ALL_PERMISSIONS)
    if user.role:
        return list(user.role.permissions or [])
    return []


# ---------- auth ----------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AcceptInviteRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=200)
    full_name: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=200)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=200)


# ---------- users / roles ----------

class RoleBrief(BaseModel):
    id: uuid.UUID
    name: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: RoleBrief | None
    is_superadmin: bool
    is_active: bool
    status: str
    must_change_password: bool
    last_login_at: datetime | None
    created_at: datetime
    permissions: list[str]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str = ""
    role_id: uuid.UUID | None = None
    # Only an existing SuperAdmin may set this; superadmins ignore role_id.
    is_superadmin: bool = False


class UpdateUserRequest(BaseModel):
    full_name: str | None = None
    role_id: uuid.UUID | None = None
    is_active: bool | None = None
    is_superadmin: bool | None = None


class InviteResult(BaseModel):
    user: UserOut
    invite_link: str | None
    email_sent: bool


class ResetResult(BaseModel):
    reset_link: str | None
    email_sent: bool


class RoleOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    permissions: list[str]
    is_system: bool
    user_count: int = 0
    created_at: datetime


class CreateRoleRequest(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str = ""
    permissions: list[str] = []


class UpdateRoleRequest(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    description: str | None = None
    permissions: list[str] | None = None


class PermissionOut(BaseModel):
    key: str
    label: str


# ---------- chats ----------

class OwnerBrief(BaseModel):
    id: uuid.UUID
    email: str


class ChatOwnerStat(BaseModel):
    """A user who owns chats — for the oversight (chats.read_all) user picker."""

    id: uuid.UUID
    email: str
    full_name: str
    chat_count: int


class ChatSummary(BaseModel):
    id: uuid.UUID
    title: str
    provider: str | None
    created_at: datetime
    updated_at: datetime
    message_count: int
    owner: OwnerBrief | None = None


class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class ChatDetail(BaseModel):
    id: uuid.UUID
    title: str
    provider: str | None
    state: dict
    messages: list[ChatMessageOut]
    owner: OwnerBrief | None = None


class RenameChatRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class CompactResult(BaseModel):
    """Result of compacting a chat's context."""

    folded: int  # messages folded into the summary this call
    kept: int  # recent messages kept verbatim in the model context
    total_messages: int  # full history size (all preserved in the DB)
    has_summary: bool  # whether the chat now carries a compaction summary


class AuditOut(BaseModel):
    id: uuid.UUID
    actor_email: str
    action: str
    target_type: str | None
    target_id: str | None
    detail: dict
    ip: str | None
    created_at: datetime


# ---------- serializers (ORM -> DTO) ----------

def user_out(u: "dbm.User") -> UserOut:
    return UserOut(
        id=u.id,
        email=u.email,
        full_name=u.full_name,
        role=RoleBrief(id=u.role.id, name=u.role.name) if u.role else None,
        is_superadmin=u.is_superadmin,
        is_active=u.is_active,
        status=u.status,
        must_change_password=u.must_change_password,
        last_login_at=u.last_login_at,
        created_at=u.created_at,
        permissions=effective_permissions(u),
    )


def role_out(r: "dbm.Role", user_count: int = 0) -> RoleOut:
    return RoleOut(
        id=r.id,
        name=r.name,
        description=r.description,
        permissions=list(r.permissions or []),
        is_system=r.is_system,
        user_count=user_count,
        created_at=r.created_at,
    )
