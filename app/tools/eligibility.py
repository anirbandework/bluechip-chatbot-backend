"""`evaluate_merge_eligibility` tool implementation.

A thin async wrapper around the deterministic merge-eligibility logic in
`knowledge.decision_rules`. **Eligibility is NEVER decided here or by the model**
— this module only validates/normalises the tool input, delegates the actual
decision to `decision_rules.evaluate(...)`, mirrors the result onto the session
decision state (so the frontend decision panel updates), and returns the §3.1
result dict verbatim.

No I/O and no network at import time.
"""

from __future__ import annotations

from typing import Any

from ..knowledge import decision_rules

# Allowed values for the co-brand linkage enum (CONTRACTS §3.1).
_COBRAND_LINKAGE_VALUES: frozenset[str] = frozenset({"none", "primary", "secondary"})


def _as_bool(value: Any) -> bool:
    """Coerce a tool-input value to a strict ``bool``.

    The model supplies JSON booleans, but be defensive about the common
    string/number stand-ins ("true"/"false"/1/0) so a slightly-off input never
    silently flips the deterministic decision.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "y"}
    return bool(value)


def _apply_state(session: Any, eligibility: dict, checklist: list[dict]) -> None:
    """Mirror the eligibility result + checklist onto ``session.state``.

    Writes ``session.state.eligibility`` (the §5 subset of the result) and
    ``session.state.checklist`` so the frontend decision panel reflects the
    latest evaluation. Supports both attribute-style state (the contract's
    ``SessionState`` model) and a plain-dict state, and degrades gracefully if
    there is no session/state at all.
    """
    if session is None:
        return
    state = getattr(session, "state", None)
    if state is None:
        return

    # The §5 eligibility shape is a subset of the full §3.1 result dict.
    eligibility_state = {
        "decision": eligibility["decision"],
        "reason_code": eligibility["reason_code"],
        "explanation": eligibility["explanation"],
        "requires_program_ops_discretion": eligibility[
            "requires_program_ops_discretion"
        ],
    }

    if isinstance(state, dict):
        state["eligibility"] = eligibility_state
        state["checklist"] = checklist
    else:
        setattr(state, "eligibility", eligibility_state)
        setattr(state, "checklist", checklist)


async def evaluate_merge_eligibility(tool_input: dict, session: Any) -> dict:
    """Decide if a BluChip account merge is permissible (deterministic).

    Validates the model-supplied ``tool_input``, delegates the decision to
    ``decision_rules.evaluate(...)``, updates ``session.state.eligibility`` and
    ``session.state.checklist`` (via ``decision_rules.CHECKLIST_RULES``) so the
    frontend panel updates, and returns the §3.1 result dict.

    Args:
        tool_input: Already-parsed dict from the model. Expected keys:
            ``name_match``, ``dob_match``, ``both_verified``,
            ``secondary_has_ibc_balance`` (all booleans), ``cobrand_linkage``
            (one of "none"|"primary"|"secondary"), and optionally
            ``member_agrees_make_cobrand_primary`` (boolean, default False).
        session: The current ``Session`` (or ``None``). Its ``state`` is updated
            in place when present.

    Returns:
        The §3.1 result dict: ``decision``, ``reason_code``, ``explanation``,
        ``recommended_template_id``, ``requires_program_ops_discretion``.
    """
    # --- Validate / normalise inputs -------------------------------------
    name_match = _as_bool(tool_input.get("name_match"))
    dob_match = _as_bool(tool_input.get("dob_match"))
    both_verified = _as_bool(tool_input.get("both_verified"))
    secondary_has_ibc_balance = _as_bool(tool_input.get("secondary_has_ibc_balance"))

    cobrand_linkage = tool_input.get("cobrand_linkage", "none")
    if not isinstance(cobrand_linkage, str):
        cobrand_linkage = "none"
    cobrand_linkage = cobrand_linkage.strip().lower()
    if cobrand_linkage not in _COBRAND_LINKAGE_VALUES:
        # Unknown linkage value: fail closed to "none" so we never silently
        # treat an unrecognised value as the merge-blocking "secondary" case.
        cobrand_linkage = "none"

    member_agrees_make_cobrand_primary = _as_bool(
        tool_input.get("member_agrees_make_cobrand_primary", False)
    )

    # --- Deterministic decision (model never decides) --------------------
    result = decision_rules.evaluate(
        name_match=name_match,
        dob_match=dob_match,
        both_verified=both_verified,
        secondary_has_ibc_balance=secondary_has_ibc_balance,
        cobrand_linkage=cobrand_linkage,
        member_agrees_make_cobrand_primary=member_agrees_make_cobrand_primary,
    )

    # --- Mirror onto session state for the frontend panel ----------------
    checklist = decision_rules.CHECKLIST_RULES(
        name_match=name_match,
        dob_match=dob_match,
        both_verified=both_verified,
        secondary_has_ibc_balance=secondary_has_ibc_balance,
        cobrand_linkage=cobrand_linkage,
    )
    _apply_state(session, result, checklist)

    return result
