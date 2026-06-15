"""Interactive form tools.

Two kinds of click-to-fill cards are produced here and surfaced in the chat as a
``form`` SSE event:

1. **Intake** — ``request_intake_form`` shows ONLY the merge facts the next
   decision needs (never a fixed "ask everything" card). The model passes the
   subset of ``items`` it still needs; the form is assembled from
   :data:`INTAKE_ITEMS`. The boolean/choice keys match
   ``evaluate_merge_eligibility``'s inputs exactly.
2. **Complete the draft** — ``build_fields_form`` turns a rendered template's
   ``missing_fields`` into a card so the agent fills them by typing/clicking
   instead of in prose.

The form spec is DETERMINISTIC and defined here — the model only *triggers* it
and chooses which items to collect; it never invents fields. The agent's filled
answers come back as an ordinary user message.
"""

from __future__ import annotations

from typing import Any

FORM_ID = "merge_intake"

# --------------------------------------------------------------------------- #
# Intake building blocks. The model requests ONLY the items the NEXT decision
# needs; the card is assembled from this registry, so it is never a fixed form.
# --------------------------------------------------------------------------- #

# Companions auto-added whenever cobrand_linkage is requested (shown via showIf).
_COBRAND_COMPANIONS: list[dict] = [
    {
        "key": "cobrand_bank",
        "label": "Issuing bank",
        "type": "text",
        "placeholder": "e.g. HDFC Bank",
        "showIf": {"field": "cobrand_linkage", "in": ["primary", "secondary"]},
    },
    {
        # Only the secondary-linked branch is gated on the member's agreement to
        # make that account Primary (decision_rules): secondary + agree ->
        # conditional/OK, secondary + not -> co-brand denial.
        "key": "cobrand_make_primary",
        "label": "The co-brand card is on the secondary account — does the member "
        "agree to make that account the Primary?",
        "type": "boolean",
        "allowRemark": True,
        "showIf": {"field": "cobrand_linkage", "in": ["secondary"]},
    },
]

# item key -> {"section": <id>, "field": <spec>, "companions"?: [<spec>, ...]}
INTAKE_ITEMS: dict[str, dict] = {
    "from_registered_email": {
        "section": "checks",
        "field": {
            "key": "from_registered_email",
            "label": "Was the merge request received from the member's registered email?",
            "type": "boolean",
            "required": True,
            "allowRemark": True,
        },
    },
    "name_match": {
        "section": "checks",
        "field": {
            "key": "name_match",
            "label": "Do the names on both accounts match?",
            "type": "boolean",
            "required": True,
            "allowRemark": True,
        },
    },
    "dob_match": {
        "section": "checks",
        "field": {
            "key": "dob_match",
            "label": "Do the dates of birth on both accounts match?",
            "type": "boolean",
            "required": True,
            "allowRemark": True,
        },
    },
    "both_verified": {
        "section": "checks",
        "field": {
            "key": "both_verified",
            "label": "Are both accounts in 'Verified' status?",
            "type": "boolean",
            "required": True,
            "allowRemark": True,
        },
    },
    "secondary_has_ibc_balance": {
        "section": "checks",
        "field": {
            "key": "secondary_has_ibc_balance",
            "label": "Does the secondary account have an IBC balance?",
            "type": "boolean",
            "required": True,
            "allowRemark": True,
        },
    },
    "cobrand_linkage": {
        "section": "cobrand",
        "field": {
            "key": "cobrand_linkage",
            "label": "Is a co-brand credit card linked to either account?",
            "type": "choice",
            "required": True,
            "options": [
                {"value": "none", "label": "None"},
                {"value": "primary", "label": "Primary account"},
                {"value": "secondary", "label": "Secondary account"},
            ],
        },
        "companions": _COBRAND_COMPANIONS,
    },
    "retain_mobile": {
        "section": "intent",
        "field": {
            "key": "retain_mobile",
            "label": "Which mobile number does the member wish to retain? "
            "(this becomes the Primary account)",
            "type": "choice",
            "options": [
                {"value": "primary", "label": "Primary account's mobile"},
                {"value": "secondary", "label": "Secondary account's mobile"},
            ],
        },
    },
    "merge_reason": {
        "section": "intent",
        "field": {
            "key": "merge_reason",
            "label": "Member's reason / intent for the merge",
            "type": "textarea",
            "placeholder": "Why does the member want to merge the accounts?",
        },
    },
}

# Keys the model may request (drives the tool's enum + defensive validation).
INTAKE_ITEM_KEYS: list[str] = list(INTAKE_ITEMS.keys())

# Optional pair section with both accounts' raw details (only when requested).
_ACCOUNT_DETAILS_SECTION: dict = {
    "id": "accounts",
    "title": "Account details",
    "description": "Read these off the two BluChip accounts.",
    "layout": "pair",
    "columns": [
        {"key": "primary", "label": "Primary account"},
        {"key": "secondary", "label": "Secondary account"},
    ],
    "fields": [
        {"key": "membership_number", "label": "Membership number", "type": "text"},
        {"key": "registered_name", "label": "Registered name", "type": "text"},
        {"key": "date_of_birth", "label": "Date of birth", "type": "text", "placeholder": "DD/MM/YYYY"},
        {"key": "registered_mobile", "label": "Registered mobile", "type": "text"},
        {"key": "registered_email", "label": "Registered email", "type": "text"},
    ],
}

_SECTION_META: dict[str, dict] = {
    "checks": {
        "id": "checks",
        "title": "Checks",
        "description": "These determine eligibility — please confirm each.",
    },
    "cobrand": {"id": "cobrand", "title": "Co-brand credit card"},
    "intent": {"id": "intent", "title": "Member intent"},
}
_SECTION_ORDER = ["checks", "cobrand", "intent"]

# Fallback when the model triggers the card without naming items.
_DEFAULT_ITEMS = [
    "name_match",
    "dob_match",
    "both_verified",
    "secondary_has_ibc_balance",
    "cobrand_linkage",
]


def build_intake_form(
    items,
    *,
    account_details: bool = False,
    title: str | None = None,
    intro: str | None = None,
) -> dict | None:
    """Assemble a merge-intake card from just the requested item keys.

    Unknown/duplicate keys are ignored. Co-brand companions (issuing bank +
    make-Primary) are added automatically when ``cobrand_linkage`` is requested.
    Returns ``None`` when nothing valid was requested.
    """
    buckets: dict[str, list] = {}
    seen: set[str] = set()
    for key in items or []:
        spec = INTAKE_ITEMS.get(key)
        if spec is None or key in seen:
            continue
        seen.add(key)
        section = spec["section"]
        buckets.setdefault(section, []).append(spec["field"])
        for companion in spec.get("companions", []):
            buckets[section].append(companion)

    sections: list[dict] = []
    if account_details:
        sections.append(_ACCOUNT_DETAILS_SECTION)
    for section_id in _SECTION_ORDER:
        fields = buckets.get(section_id)
        if fields:
            sections.append({**_SECTION_META[section_id], "fields": fields})

    if not sections:
        return None

    return {
        "form_id": FORM_ID,
        "title": title or "Merge account — details needed",
        "description": intro
        or "Confirm the checks below (add a remark where it helps), then submit.",
        "submit_label": "Submit details",
        "submit_intro": "Submitted merge details:",
        "sections": sections,
        "remarks": {
            "key": "remarks",
            "label": "Additional remarks (optional)",
            "placeholder": "Anything else relevant to this case…",
        },
    }


async def request_intake_form(tool_input: dict, session: Any) -> dict:
    """Display an intake card with ONLY the requested facts.

    ``tool_input``: ``{"items": [<key>, ...], "account_details"?: bool,
    "title"?: str, "intro"?: str}``. ``items`` should be only the facts the next
    decision needs; if omitted, the core eligibility checks are used. The
    provider emits ``result["form"]`` as a ``form`` SSE event and strips it from
    what the model sees.
    """
    items = tool_input.get("items")
    if isinstance(items, str):
        items = [items]
    items = [k for k in (items or []) if k in INTAKE_ITEMS]
    if not items:
        items = list(_DEFAULT_ITEMS)

    form = build_intake_form(
        items,
        account_details=bool(tool_input.get("account_details", False)),
        title=tool_input.get("title"),
        intro=tool_input.get("intro"),
    )
    if form is None:
        return {
            "status": "no_fields",
            "instruction": "No intake fields matched; ask the agent directly instead.",
        }
    return {
        "status": "form_displayed",
        "form": form,
        "instruction": (
            "The intake card is now shown to the agent in the chat. Do NOT call "
            "any other tool now and do NOT evaluate eligibility yet. Reply with "
            "ONE short line asking the agent to fill it in and submit; the answers "
            "arrive as the next message."
        ),
    }


# --------------------------------------------------------------------------- #
# "Complete the draft" form — built dynamically from a template's missing_fields
# so the agent fills them by typing/clicking instead of in prose. Field keys are
# the template placeholder names; each maps to a friendly label + the right input
# type (e.g. call_reason → a choice, member name → text).
# --------------------------------------------------------------------------- #

# Friendly metadata for every placeholder used across the SOP email templates.
# Anything not listed falls back to a humanized label + a text input.
FIELD_META: dict[str, dict] = {
    "member_last_name": {"label": "Member's last name", "placeholder": "e.g. Kumar"},
    "agent_name": {"label": "Your name (agent)", "placeholder": "e.g. Asha"},
    "primary_phone": {"label": "Primary account — mobile number", "placeholder": "10-digit mobile"},
    "secondary_phone": {"label": "Secondary account — mobile number", "placeholder": "10-digit mobile"},
    "primary_email": {"label": "Primary account — email", "placeholder": "name@example.com"},
    "other_account_email": {"label": "Other account's email", "placeholder": "name@example.com"},
    "primary_membership_no": {"label": "Primary account — membership number"},
    "secondary_membership_no": {"label": "Secondary account — membership number"},
    "cobrand_bank_name": {"label": "Co-brand card — issuing bank", "placeholder": "e.g. HDFC Bank"},
    "call_time": {"label": "Time of the call attempt", "placeholder": "e.g. 3:45 PM, 12 Jun"},
    "call_reason": {
        "label": "Outcome of the call attempt",
        "type": "choice",
        "options": [
            {"value": "Unanswered", "label": "Unanswered"},
            {"value": "not reachable", "label": "Not reachable"},
            {"value": "switched off", "label": "Switched off"},
            {"value": "busy", "label": "Busy"},
        ],
    },
    "account1_membership_no": {"label": "Account 1 — membership number"},
    "account1_name": {"label": "Account 1 — name on account"},
    "account1_ibc_balance": {"label": "Account 1 — IBC balance"},
    "account2_membership_no": {"label": "Account 2 — membership number"},
    "account2_name": {"label": "Account 2 — name on account"},
    "account2_ibc_balance": {"label": "Account 2 — IBC balance"},
}

_ABBREV = {"no": "number", "ibc": "IBC", "dob": "DOB", "id": "ID"}


def _humanize(name: str) -> str:
    words = (name or "").replace("__", " ").replace("_", " ").split()
    out = [_ABBREV.get(w.lower(), w.capitalize()) for w in words]
    return " ".join(out) if out else (name or "")


def _field_spec(name: str) -> dict:
    meta = FIELD_META.get(name, {})
    spec: dict = {
        "key": name,
        "label": meta.get("label") or _humanize(name),
        "type": meta.get("type", "text"),
    }
    if meta.get("placeholder"):
        spec["placeholder"] = meta["placeholder"]
    if meta.get("options"):
        spec["options"] = meta["options"]
    return spec


def build_fields_form(template_id: str | None, missing_fields) -> dict | None:
    """Build a 'complete the draft' form from a template's missing placeholders.

    Returns ``None`` when there is nothing missing. Fields are optional — the
    agent fills what applies (e.g. call details only when the member was not
    reached) and submits; the model re-renders the template with the values.
    """
    names = [n for n in (missing_fields or []) if n]
    if not names:
        return None

    # Local import avoids any import-order coupling with the tools package.
    from app.knowledge.email_templates import template_label

    label = template_label(template_id) if template_id else "email"
    return {
        "form_id": f"draft_fields:{template_id or ''}",
        "title": f"Complete the {label}",
        "description": (
            "Fill the remaining details and submit — I'll finish the draft. "
            "Leave any that don't apply (e.g. call details when the member was "
            "reached) blank."
        ),
        "submit_label": "Update draft",
        "submit_intro": (
            f"Here are the remaining details to complete the {label} draft. "
            "Please re-render that template with these values:"
        ),
        "sections": [
            {
                "id": "fields",
                "title": "Remaining details",
                "fields": [_field_spec(n) for n in names],
            }
        ],
    }
