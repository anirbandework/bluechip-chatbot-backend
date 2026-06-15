"""Tool REGISTRY (Anthropic tool schemas) and the async dispatcher.

This module exports:
- ``REGISTRY``: a ``list[dict]`` of Anthropic tool schemas
  (``{"name", "description", "input_schema"}``) — one per tool.
- ``dispatch(name, tool_input, session)``: an async router that calls the
  matching implementation and returns a JSON-serializable ``dict``.

Per CONTRACTS §3 the tool *logic* lives in the sibling implementation modules
(``eligibility``, ``templates``, ``account``, ``outcomes``, ``masking``). This
module only wires schemas to those implementations; it never redefines logic.

Descriptions are deliberately prescriptive about WHEN to call each tool because
Opus 4.8 reaches for tools conservatively.
"""

from __future__ import annotations

from typing import Any

from . import account, eligibility, forms, knowledge, masking, outcomes, templates

# ---------------------------------------------------------------------------
# Tool schemas (Anthropic format). input_schema fields match CONTRACTS §3.1-§3.5
# EXACTLY — do not change names, types, enums, or required lists.
# ---------------------------------------------------------------------------

REGISTRY: list[dict] = [
    {
        "name": "request_intake_form",
        "description": (
            "Show the agent an interactive, click-to-fill INTAKE CARD to collect "
            "merge facts — but ONLY the facts the NEXT decision needs, never a "
            "fixed 'ask everything' form. Pass `items` with just the checks you "
            "still need (omit any the agent already gave). Because a name mismatch "
            "alone denies the merge, START a fresh case by requesting only "
            '["name_match"]; once the names match, request the remaining checks '
            "you still need. PREFER THIS over asking for facts in prose. After "
            "calling it, reply with ONE short line telling the agent to fill it in "
            "and submit, then END your turn — do NOT call evaluate_merge_eligibility "
            "or guess any fact; the agent's answers arrive as the next message. "
            "SKIP this entirely if the agent already stated the facts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "string", "enum": forms.INTAKE_ITEM_KEYS},
                    "description": (
                        "Which facts to collect — include ONLY what the next "
                        "decision needs and that you don't already know. e.g. "
                        '["name_match"] to start; once names match, '
                        '["dob_match", "both_verified", "secondary_has_ibc_balance", '
                        '"cobrand_linkage"]. Available: from_registered_email, '
                        "name_match, dob_match, both_verified, "
                        "secondary_has_ibc_balance, cobrand_linkage (auto-adds the "
                        "issuing bank + make-Primary follow-ups), retain_mobile, "
                        "merge_reason."
                    ),
                },
                "account_details": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Also collect both accounts' raw details (membership no, "
                        "name, DOB, mobile, email). Usually UNNECESSARY — the email "
                        "draft collects the specific fields it needs. Set true only "
                        "if you genuinely need the raw values now."
                    ),
                },
                "title": {
                    "type": "string",
                    "description": "Optional custom card title for the agent.",
                },
                "intro": {
                    "type": "string",
                    "description": "Optional one-line card description for the agent.",
                },
            },
            "required": ["items"],
        },
    },
    {
        "name": "evaluate_merge_eligibility",
        "description": (
            "Decide whether merging two IndiGo BluChip accounts is permissible. "
            "This is PURE DETERMINISTIC LOGIC — you must NEVER judge eligibility "
            "yourself. Call this tool the moment you have gathered (or can infer "
            "from lookup_member_account / the agent's input) the five account "
            "facts: whether the names match, whether the dates of birth match, "
            "whether both accounts are in 'Verified' status, whether the secondary "
            "account has an IBC balance, and where any co-brand card is linked "
            "(none/primary/secondary). Use its returned decision, reason_code, and "
            "recommended_template_id to drive the next step and to choose which "
            "email template to render. Re-call it if any of these facts change."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name_match": {
                    "type": "boolean",
                    "description": "Names on both accounts match.",
                },
                "dob_match": {
                    "type": "boolean",
                    "description": "Date of birth on both accounts match.",
                },
                "both_verified": {
                    "type": "boolean",
                    "description": "Both accounts are in 'Verified' status.",
                },
                "secondary_has_ibc_balance": {
                    "type": "boolean",
                    "description": "The secondary account has an IBC balance.",
                },
                "cobrand_linkage": {
                    "type": "string",
                    "enum": ["none", "primary", "secondary"],
                    "description": "Which account a co-brand card is linked to.",
                },
                "member_agrees_make_cobrand_primary": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Optional. True if the member agreed to make the "
                        "co-brand-linked account the Primary account."
                    ),
                },
            },
            "required": [
                "name_match",
                "dob_match",
                "both_verified",
                "secondary_has_ibc_balance",
                "cobrand_linkage",
            ],
        },
    },
    {
        "name": "mask_credential",
        "description": (
            "Mask a single member credential (email or phone) for customer-facing "
            "disclosure. Call this whenever you need to refer to a member's email "
            "or phone number in any text the member will see — the SOP allows only "
            "the first 3 letters of an email and the last 3 digits of a phone "
            "number to be disclosed. Note: render_email_template already auto-masks "
            "credential fields, so use this tool only for ad-hoc masking outside a "
            "rendered template."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "string",
                    "description": "The raw credential value to mask.",
                },
                "kind": {
                    "type": "string",
                    "enum": ["email", "phone"],
                    "description": "Whether the value is an email or a phone number.",
                },
            },
            "required": ["value", "kind"],
        },
    },
    {
        "name": "render_email_template",
        "description": (
            "Produce the final email text for one of the 10 SOP templates "
            "(T1..T10). SOP-required masking is applied automatically. Call this "
            "whenever you need to draft ANY email to the member or to Program Ops "
            "— never hand-write email copy yourself, because the legally-worded "
            "sentences and masking rules are enforced here. First use "
            "evaluate_merge_eligibility to learn the recommended_template_id, then "
            "call this with that template_id and the known fields. Any returned "
            "missing_fields tell you what to ask the agent for before the draft is "
            "complete."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "template_id": {
                    "type": "string",
                    "description": "The template to render, one of T1..T10.",
                },
                "fields": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": (
                        "Map of placeholder field names to real string values. "
                        "Provide the actual values; the SOP-required masking is "
                        "applied automatically (e.g. the other account's email in "
                        "T2). Credentials shown to the verified account owner, and "
                        "the internal T10, are kept in full."
                    ),
                },
            },
            "required": ["template_id", "fields"],
        },
    },
    {
        "name": "lookup_member_account",
        "description": (
            "Attempt to fetch account facts for a merge. IMPORTANT: in this build "
            "there is NO live CRM/LMS connection — this ALWAYS returns "
            "'not available' and never returns real or invented account data. Do "
            "NOT rely on it for member details, and never present its result as a "
            "real account. Instead, ASK THE AGENT to read the facts (name, DOB, "
            "'Verified' status, IBC balance, co-brand linkage) from their CRM/LMS "
            "or get them from the verified member. Never state account details as "
            "real unless the agent gave them to you."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "identifier": {
                    "type": "string",
                    "description": (
                        "Membership number, email, or phone identifying the member."
                    ),
                },
            },
            "required": ["identifier"],
        },
    },
    {
        "name": "record_outcome",
        "description": (
            "Append an auditable event to the session timeline (e.g. a call "
            "attempt, DPA pass/fail, consent received, escalation to Program Ops, "
            "or resolution). Call this every time one of these milestones actually "
            "happens during the conversation so the decision panel and audit log "
            "stay accurate. Do not use it to record speculative or future events."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "event": {
                    "type": "string",
                    "enum": [
                        "call_attempt",
                        "dpa_passed",
                        "dpa_failed",
                        "consent_received",
                        "escalated_to_ops",
                        "resolved",
                    ],
                    "description": "The milestone event that occurred.",
                },
                "detail": {
                    "type": "string",
                    "description": "Optional free-text detail about the event.",
                },
            },
            "required": ["event"],
        },
    },
    {
        "name": "search_knowledge",
        "description": (
            "Search the IndiGo BluChip knowledge base (the program Terms & "
            "Conditions, the earning/accrual FAQs, and other reference documents) "
            "for the rules relevant to a question. CALL THIS for ANY question "
            "about the BluChip programme beyond the merge workflow — earning, "
            "redemption / spending points, points expiry, tiers & qualification, "
            "enrolment, nominees, deceased member, fraud, fees, partners, account "
            "changes, or anything in the T&C. Use a short, focused query of the "
            "key terms. Answer ONLY from the text it returns and cite the section; "
            "if it returns nothing relevant, tell the agent you don't have that "
            "information — never invent policy or numbers."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Focused search query of the key terms, e.g. 'tier "
                        "qualification criteria', 'deceased member points "
                        "transfer', 'retro claim window', 'change registered email'."
                    ),
                },
            },
            "required": ["query"],
        },
    },
]


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

async def dispatch(name: str, tool_input: dict, session: Any) -> dict:
    """Route a tool call to its implementation and return a JSON-serializable dict.

    ``tool_input`` is the already-parsed input dict from the model. An unknown
    tool name returns ``{"error": ...}`` rather than raising.
    """
    if name == "request_intake_form":
        return await forms.request_intake_form(tool_input, session)

    if name == "evaluate_merge_eligibility":
        return await eligibility.evaluate_merge_eligibility(tool_input, session)

    if name == "mask_credential":
        kind = tool_input.get("kind")
        value = tool_input.get("value", "")
        if kind == "email":
            return {"masked": masking.mask_email(value)}
        if kind == "phone":
            return {"masked": masking.mask_phone(value)}
        return {"error": f"Unknown mask_credential kind: {kind!r}"}

    if name == "render_email_template":
        return await templates.render_email_template(tool_input, session)

    if name == "lookup_member_account":
        return await account.lookup_member_account(tool_input, session)

    if name == "record_outcome":
        return await outcomes.record_outcome(tool_input, session)

    if name == "search_knowledge":
        return await knowledge.search_knowledge(tool_input, session)

    return {"error": f"Unknown tool: {name!r}"}
