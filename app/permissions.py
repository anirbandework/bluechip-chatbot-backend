"""Permission keys and seeded default roles for the dynamic RBAC system.

SuperAdmin implicitly holds every permission. Other users get exactly the
permissions of their assigned role. SuperAdmin can compose new roles from these
keys at runtime.
"""

from __future__ import annotations

# Canonical permission keys the backend understands (key -> human label).
PERMISSIONS: dict[str, str] = {
    "users.read": "View users",
    "users.create": "Create / invite users",
    "users.update": "Edit users (name, role, enable / disable)",
    "users.delete": "Delete users",
    "roles.read": "View roles",
    "roles.manage": "Create / edit / delete roles",
    "chats.use": "Use the assistant (create & chat)",
    "chats.read_all": "View other users' chats (oversight)",
    "audit.read": "View the audit log",
}

ALL_PERMISSIONS: list[str] = list(PERMISSIONS)

# Seeded on first boot. Editable/deletable afterwards (they're just convenient
# starting points — the SuperAdmin can define any roles they like).
DEFAULT_ROLES: list[dict] = [
    {
        "name": "Admin",
        "description": "Manage users & roles, oversee all chats, view the audit log.",
        "permissions": [
            "users.read",
            "users.create",
            "users.update",
            "users.delete",
            "roles.read",
            "chats.use",
            "chats.read_all",
            "audit.read",
        ],
    },
    {
        "name": "Agent",
        "description": "Use the assistant and manage their own chats.",
        "permissions": ["chats.use"],
    },
]
