"""Deterministic merge-eligibility logic for the BluChip Agent-Assist bot.

This module is the single source of truth for *whether a merge is permissible*.
Eligibility is NEVER decided by the model — the model must call the
`evaluate_merge_eligibility` tool, which delegates to `evaluate()` here.

The logic mirrors the merge-account flowchart (CONTRACTS §3.1). Each branch
below is annotated with the flowchart node it represents:

    1. Name match?              -> NO  : not_allowed  (NAME_MISMATCH, T7)
    2. DOB match?               -> NO  : conditional  (DOB_MISMATCH, Program Ops decides)
    3. Both accounts Verified?  -> NO  : not_allowed  (NOT_VERIFIED, T5)
    4. Co-brand on secondary?   -> YES : not_allowed  (COBRAND_ON_SECONDARY, T6)
                                          unless the member agrees to make the
                                          co-brand (secondary) account Primary,
                                          in which case -> conditional (OK).
    5. Otherwise                       : allowed      (OK, proceed to consent +
                                          Program Ops path).

`DIFFERENT_IDENTITIES` is exposed for callers that explicitly detect distinct
identities; it is treated like `NAME_MISMATCH` (not_allowed). The flowchart's
default "family accounts / different identities" path is reached via
`name_match == False`.

No side effects on import; this module performs no I/O and holds no state.
"""

from __future__ import annotations

# Enum of every reason code this module can emit (CONTRACTS §3.1).
REASON_CODES: list[str] = [
    "OK",
    "NAME_MISMATCH",
    "DOB_MISMATCH",
    "NOT_VERIFIED",
    "COBRAND_ON_SECONDARY",
    "DIFFERENT_IDENTITIES",
]


def evaluate(
    name_match: bool,
    dob_match: bool,
    both_verified: bool,
    secondary_has_ibc_balance: bool,
    cobrand_linkage: str,
    member_agrees_make_cobrand_primary: bool = False,
) -> dict:
    """Decide whether a BluChip account merge is permissible.

    Pure, deterministic function — given the same facts it always returns the
    same result. Maps directly onto the merge-account flowchart (see module
    docstring for the branch-to-node mapping).

    Args:
        name_match: Names on both accounts match.
        dob_match: DOB on both accounts match.
        both_verified: Both accounts are in 'Verified' status.
        secondary_has_ibc_balance: Secondary account carries an IBC balance.
        cobrand_linkage: One of "none" | "primary" | "secondary" — which account
            the co-brand credit card privileges are linked to.
        member_agrees_make_cobrand_primary: Whether the member has agreed to make
            the co-brand-linked (secondary) account the Primary instead.

    Returns:
        dict with keys: decision, reason_code, explanation,
        recommended_template_id, requires_program_ops_discretion.
    """
    # Branch 1 — Name match? NO -> denial for name mismatch (flowchart: T7).
    # Family accounts / different identities also land here via name_match=False.
    if not name_match:
        return {
            "decision": "not_allowed",
            "reason_code": "NAME_MISMATCH",
            "explanation": (
                "Names registered on the two accounts do not match. Program "
                "guidelines require the registered name to be consistent across "
                "both accounts, so the merge cannot be processed. Send the "
                "name-mismatch denial (T7)."
            ),
            "recommended_template_id": "T7",
            "requires_program_ops_discretion": False,
        }

    # Branch 2 — DOB match? NO (with name matching) -> Program Ops discretion.
    # No template here: Program Ops decides whether to proceed.
    if not dob_match:
        return {
            "decision": "conditional",
            "reason_code": "DOB_MISMATCH",
            "explanation": (
                "Names match but the date of birth differs between the two "
                "accounts. This requires Program Ops discretion to decide "
                "whether the merge may proceed; do not draft a customer denial "
                "or approval until Program Ops advises."
            ),
            "recommended_template_id": None,
            "requires_program_ops_discretion": True,
        }

    # Branch 3 — Both accounts Verified? NO -> denial, DPA/verification failed
    # on the other account (flowchart: T5).
    if not both_verified:
        return {
            "decision": "not_allowed",
            "reason_code": "NOT_VERIFIED",
            "explanation": (
                "Verification (DPA / security-question check) on the other "
                "IndiGo BluChip account could not be successfully completed, so "
                "the merge cannot be processed. Send the verification-failed "
                "denial (T5)."
            ),
            "recommended_template_id": "T5",
            "requires_program_ops_discretion": False,
        }

    # Branch 4 — Co-brand privileges linked to the SECONDARY account.
    if cobrand_linkage == "secondary":
        if member_agrees_make_cobrand_primary:
            # Member agrees to make the co-brand (secondary) account Primary.
            # Proceed with the secondary-as-primary path.
            return {
                "decision": "conditional",
                "reason_code": "OK",
                "explanation": (
                    "Co-brand privileges are linked to the secondary account, "
                    "but the member has agreed to make that account the Primary. "
                    "Proceed with the secondary-as-primary path: collect consent "
                    "from both accounts and route to Program Ops."
                ),
                "recommended_template_id": None,
                "requires_program_ops_discretion": False,
            }
        # Member has not (yet) agreed -> offer to make that account Primary (T6).
        return {
            "decision": "not_allowed",
            "reason_code": "COBRAND_ON_SECONDARY",
            "explanation": (
                "Co-brand credit card privileges and benefits are linked to the "
                "other (secondary) account. Merging as requested would "
                "discontinue those benefits, so the merge cannot be processed as "
                "is. Offer to make that account the Primary instead (T6)."
            ),
            "recommended_template_id": "T6",
            "requires_program_ops_discretion": False,
        }

    # Branch 5 — Default allowed path: name + DOB match, both verified, and
    # co-brand is none/primary. Proceed to consent + Program Ops path.
    return {
        "decision": "allowed",
        "reason_code": "OK",
        "explanation": (
            "Names and dates of birth match, both accounts are verified, and "
            "co-brand linkage does not block the merge. Proceed: confirm the "
            "Primary account, collect consent from both registered emails, then "
            "route the execution request to Program Ops."
        ),
        "recommended_template_id": None,
        "requires_program_ops_discretion": False,
    }


def CHECKLIST_RULES(
    name_match: bool,
    dob_match: bool,
    both_verified: bool,
    secondary_has_ibc_balance: bool,
    cobrand_linkage: str,
) -> list[dict]:
    """Build the §5 decision-panel checklist from the merge facts.

    Mirrors the "Allowed if / Not allowed if" rules so the agent sees a per-rule
    status. Returns a list of {"label", "ok"} dicts in flowchart order:
    name match, DOB match, both verified, secondary has IBC balance, co-brand
    linked to primary.

    Pure helper, no side effects.
    """
    return [
        {"label": "Name match", "ok": bool(name_match)},
        {"label": "DOB match", "ok": bool(dob_match)},
        {"label": "Both accounts verified", "ok": bool(both_verified)},
        {
            "label": "Secondary has IBC balance",
            "ok": bool(secondary_has_ibc_balance),
        },
        {
            "label": "Co-brand linked to primary",
            # OK when co-brand does not sit on the secondary account, i.e. it is
            # linked to the primary or there is no co-brand linkage at all.
            "ok": cobrand_linkage != "secondary",
        },
    ]
