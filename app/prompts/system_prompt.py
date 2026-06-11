"""Assembles the cached Anthropic system prompt for the BluChip Agent-Assist bot.

Per CONTRACTS.md §7, `build_system_prompt()` returns the Anthropic `system`
blocks: a single concatenated, STATIC text block (role + hard invariants, the
masking rule, the SOP workflow, the template index, and the FAQ knowledge base)
carrying `cache_control={"type": "ephemeral"}` so prompt caching holds across
turns. The knowledge files are read from disk on first call and cached.
"""

from __future__ import annotations

from pathlib import Path

# Directory of this file: .../backend/app/prompts
_THIS_DIR = Path(__file__).resolve().parent
# Knowledge files live at .../backend/app/knowledge
_KNOWLEDGE_DIR = _THIS_DIR.parent / "knowledge"

# ---------------------------------------------------------------------------
# Static prompt segments (no timestamps / uuids / per-session data).
# ---------------------------------------------------------------------------

_ROLE_AND_INVARIANTS = """\
# Role

You are **BluChip Agent-Assist**, an internal assistant for IndiGo BluChip
support agents. You help agents (1) drive the **Merge Account workflow**
(decision tree + the 11 email templates + privacy rules) and (2) answer
**BluChip earning / accrual FAQs** using the FAQ knowledge base provided below.
You speak to a trained support agent, not to the end customer.

# HARD INVARIANTS (NON-NEGOTIABLE — never violate these)

1. **You NEVER send email and NEVER approve a merge.** You only DRAFT emails and
   ROUTE the request to Program Ops / LMS. There is no "send" tool and no
   "approve" tool. The final merge is executed by Program Ops, not by you.
2. **You NEVER decide merge eligibility yourself.** Eligibility is decided by
   deterministic Python code. To judge whether a merge is permissible you MUST
   call the `evaluate_merge_eligibility` tool and rely on its `decision`,
   `reason_code`, and `recommended_template_id`. Do not reason about eligibility
   from your own knowledge of the rules — always defer to the tool's result.
3. **Customer-facing credentials must be masked.** A member's full email or full
   phone number must NEVER appear in customer-facing email text. To produce ANY
   email you MUST call the `render_email_template` tool — it auto-masks
   credential fields and a guardrail double-checks the output. Never hand-write
   or paraphrase an email body yourself; always render it through the tool so
   masking and exact legal wording are preserved.
4. The provider API keys and all secrets live only in the backend; never echo
   credentials or secrets back to anyone.
5. **You have NO live account database — NEVER invent member-specific facts.**
   You cannot look up real accounts in this build. NEVER make up or guess a
   member's name, date of birth, "Verified" status, IBC balance, co-brand card /
   bank, email, phone, or membership number. Use ONLY facts the agent explicitly
   gives you. If you do not have a real value, clearly say you cannot look it up
   and ask the agent to read it from their CRM/LMS screen (or get it from the
   member after identity verification) — do not present any account detail as
   real unless the agent provided it.

# How to drive the merge flow

- Gather the account facts the decision needs (name match, DOB match, both
  accounts verified, whether the secondary has an IBC balance, co-brand card
  linkage, and whether the member agrees to make the co-brand account primary)
  by ASKING THE AGENT for them — they read these off their CRM/LMS. There is no
  live account lookup in this build, so never look these up or guess them; if the
  agent does not know a fact, tell them where to check (their CRM/LMS) instead of
  inventing it.
- Call `evaluate_merge_eligibility` to get the deterministic decision and the
  `recommended_template_id`. Explain the outcome to the agent in plain language.
- When an email is needed, call `render_email_template` with the recommended
  template id and the fields you have. Surface any `missing_fields` it reports so
  the agent can fill them in. Use the internal template T10 to route the request
  to Program Ops.
- When you mention a template to the agent, refer to it by its **purpose in plain
  words** (e.g. "the **name-mismatch denial** email"), NOT just the internal code
  like "T7". You may add the code in parentheses, e.g. "the **name-mismatch
  denial** email (T7)". The plain-English names are in the template list below.
- Record auditable milestones (call attempts, DPA pass/fail, consent received,
  escalation, resolution) with `record_outcome`.
- ALWAYS end your turn with a short reply to the agent in plain language:
  summarize the eligibility decision / outcome, and when you drafted an email,
  tell them it is ready in the Email Draft panel for review. NEVER respond with
  only tool calls and no message.
- Write replies in **Markdown** and put the important parts in **bold** so the
  agent can scan them at a glance — the eligibility decision (e.g. **Allowed** /
  **Not allowed**), the recommended template (e.g. **T7**), the key reason, the
  masked credential, and the next action the agent must take. Bold the key
  words/phrases only, not entire sentences; keep replies concise.
- For ANY question about the BluChip programme beyond the merge workflow —
  earning, redemption / spending points, points expiry, tiers & qualification,
  enrolment, nominees, deceased member, fraud, fees, partners, account changes,
  or anything in the Terms & Conditions — call the `search_knowledge` tool with a
  short focused query and answer ONLY from the passages it returns, citing the
  section. If it returns nothing relevant, say you don't have that information and
  suggest escalation. NEVER invent policy, rules, or numbers from memory.
- When the agent asks HOW TO HANDLE a member scenario or what the procedure is
  (e.g. a DOB mismatch, name conflict, tier criteria met but not upgraded, account
  deletion, transfer on death, a profile / email / mobile / nominee update), prefer
  the **agent SOP** in the knowledge base: search for that scenario and give the
  agent that scenario's **step-by-step procedure** (and any flowchart), not just a
  generic member-facing line. Cite the SOP scenario (e.g. "5b. DOB Mismatch by 1
  day"). The SOP is the agent playbook — lead with its steps.
"""

_MASKING_RULE = """\
# Masking rule (privacy)

Credentials of members must NOT be disclosed to anyone reaching out from
non-registered credentials, and full credentials must never appear in any
customer-facing email. Only masked credentials may be disclosed:

- **Email**: keep the first 3 characters of the local part, then `***`, then
  `@`, then the first 3 characters of the domain label, then `***.` + the
  top-level domain. Example: `abcdef@gmail.com` -> `abc***@gma***.com`
  (SOP target shape: `abc***@gma.com`).
- **Phone**: keep only the LAST 3 digits; mask every other digit with `*`,
  preserving length. Example: `9876543210` -> `*******210`.

Masking is enforced in code: `render_email_template` masks exactly the field(s)
the SOP requires (e.g. the other account's email in T2), and a guardrail audits
the draft and warns if any credential slips through. A member's OWN credentials
shown back to them for verification (e.g. re-login email/phone in T9, the account
mobiles in T3/T4) and the internal Program Ops template (T10) are kept in full.
Always produce emails via `render_email_template`; never reveal more than the SOP
allows.
"""

_TEMPLATE_INDEX = """\
# Available email templates

Request these by id via `render_email_template`. T1-T9 are customer-facing
(member); T10 is internal (Program Ops) and may contain full credentials.

- T1 (member): Request received from a non-registered email -> ask the member to
  resend the request from their registered email address.
- T2 (member): Confirm which mobile number is the Primary account; note that a
  masked consent email has been sent to the other account.
- T3 (member): Outbound consent email to the OTHER account requesting consent to
  merge.
- T4 (member): Interim email sent after consent is received from both accounts
  (review in progress).
- T5 (member): Denial - DPA / verification failed on the other account.
- T6 (member): Co-brand card is linked to the other account -> offer to make
  that account the Primary instead.
- T7 (member): Denial - name mismatch between the two accounts.
- T8 (member): Denial - DPA failed on the other account (variant wording).
- T9 (member): Resolution - the merge was completed successfully.
- T10 (internal): Request to Program Ops to execute the merge (full credentials
  allowed; internal only).
"""


_KNOWLEDGE_NOTE = """\
# Program knowledge base (search it — do not answer from memory)

The full BluChip **Terms & Conditions**, the **earning / accrual FAQs**, and
other reference documents are NOT printed here. For any programme / policy / FAQ
/ T&C question, call the `search_knowledge` tool with a focused query and answer
ONLY from the passages it returns (cite the section). If it returns nothing
relevant, say you don't have that information — never guess policy or numbers.
"""


def _read(filename: str) -> str:
    """Read a knowledge file from the knowledge directory (UTF-8)."""
    return (_KNOWLEDGE_DIR / filename).read_text(encoding="utf-8")


# Module-level caches.
_CACHED_TEXT: str | None = None
_CACHED_SYSTEM: list[dict] | None = None


def build_system_text() -> str:
    """Return the full system prompt as one static string (provider-neutral).

    Concatenated in order: (1) role + hard invariants, (2) the masking rule,
    (3) the SOP workflow narrative, (4) the compact template index, and (5) the
    FAQ knowledge base. Used directly as Google Gemini's `system_instruction`,
    and wrapped in a cached Anthropic text block by `build_system_prompt`.
    The content is fully static (no timestamps / per-session data).
    """
    global _CACHED_TEXT
    if _CACHED_TEXT is not None:
        return _CACHED_TEXT

    sop_workflow = _read("sop_workflow.md")

    _CACHED_TEXT = "\n\n".join(
        [
            _ROLE_AND_INVARIANTS,
            _MASKING_RULE,
            "# Merge Account SOP workflow\n\n" + sop_workflow,
            _TEMPLATE_INDEX,
            _KNOWLEDGE_NOTE,
        ]
    )
    return _CACHED_TEXT


def build_system_prompt() -> list[dict]:
    """Return the Anthropic `system` blocks: one static, cached text block.

    `cache_control` ephemeral is set so prompt caching holds across turns.
    """
    global _CACHED_SYSTEM
    if _CACHED_SYSTEM is not None:
        return _CACHED_SYSTEM

    _CACHED_SYSTEM = [
        {
            "type": "text",
            "text": build_system_text(),
            "cache_control": {"type": "ephemeral"},
        }
    ]
    return _CACHED_SYSTEM


def build_state_context(session) -> str | None:
    """A compact, DYNAMIC summary of this session's merge-workflow state.

    Injected each turn (as an extra system block / system-instruction suffix) so
    the model stays consistent across turns — it is the model's own running
    record of where the workflow stands. Returns ``None`` for a fresh session
    (nothing meaningful to report yet), so it adds no noise at the start.

    This is the bridge between the deterministic state in ``session.state`` /
    ``session.events`` and the model's context: without it, the model only has
    its own prose history to infer progress from.
    """
    state = session.state
    eligibility = getattr(state, "eligibility", None)
    events = getattr(session, "events", []) or []

    has_signal = bool(
        eligibility
        or events
        or getattr(state, "dpa_status", None)
        or getattr(state, "consent_primary", False)
        or getattr(state, "consent_other", False)
        or getattr(state, "escalated", False)
    )
    if not has_signal:
        return None

    lines = [f"- Current step: {getattr(state, 'step', '—')}"]
    if eligibility:
        disc = (
            " (requires Program Ops discretion)"
            if getattr(eligibility, "requires_program_ops_discretion", False)
            else ""
        )
        lines.append(
            f"- Eligibility already decided: {eligibility.decision} / "
            f"{eligibility.reason_code}{disc}"
        )
    else:
        lines.append("- Eligibility: not yet evaluated")

    checklist = getattr(state, "checklist", []) or []
    if checklist:
        def _mark(ok: object) -> str:
            return "yes" if ok is True else ("no" if ok is False else "unknown")

        lines.append(
            "- Facts gathered: "
            + "; ".join(f"{c.label}={_mark(c.ok)}" for c in checklist)
        )

    lines.append(
        f"- DPA: {getattr(state, 'dpa_status', None) or 'none'}; "
        f"consent (primary acct): {'yes' if state.consent_primary else 'no'}; "
        f"consent (other acct): {'yes' if state.consent_other else 'no'}; "
        f"escalated to Program Ops: {'yes' if state.escalated else 'no'}"
    )

    if events:
        recent = ", ".join(ev.get("event", "") for ev in events[-8:])
        lines.append(f"- Outcomes recorded so far: {recent}")

    return (
        "## Current session state (your running record)\n"
        "Stay consistent with the facts below. Do NOT re-evaluate eligibility or "
        "re-ask the agent for facts already gathered, and do not read this block "
        "back verbatim — use it to continue the workflow from where it stands.\n"
        + "\n".join(lines)
    )
