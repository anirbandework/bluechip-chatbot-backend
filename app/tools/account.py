"""``lookup_member_account`` tool — NO live lookup in this build.

There is **no** CRM / LMS integration here. This tool deliberately returns
nothing and **never fabricates account details**: it tells the caller to obtain
the facts from the agent's real CRM/LMS screen, or from the member after identity
verification. It is the integration seam — when a real lookup is added, replace
the body with a real async call and return real values in the §3.4 shape
(``found``, ``membership_no``, ``name``, ``dob``, ``verified``, ``ibc_balance``,
``cobrand_bank``).

No I/O and no network at import time.
"""

from __future__ import annotations

from typing import Any

_NOT_CONNECTED_MESSAGE: str = (
    "No live account lookup is connected in this build, so I cannot retrieve real "
    "account details and I must not guess them. Please read the required facts "
    "(name, date of birth, 'Verified' status, IBC balance, and any co-brand card "
    "linkage) from your CRM/LMS screen — or get them from the member after "
    "identity verification — and share them so I can evaluate the merge."
)


async def lookup_member_account(tool_input: dict, session: Any) -> dict:
    """Return a clear 'not available' result — NEVER fabricated account data.

    Args:
        tool_input: Already-parsed dict from the model. Key: ``identifier``
            (membership no / email / phone).
        session: The current ``Session`` (unused; accepted to match the uniform
            tool-dispatch signature).

    Returns:
        ``{found: False, lookup_available: False, ...}`` with every fact field
        set to ``None`` and a ``message`` instructing the caller to get the facts
        from the agent / member. It never invents a name, DOB, balance, or
        co-brand bank for any identifier.
    """
    identifier = tool_input.get("identifier")
    identifier_str = str(identifier).strip() if identifier is not None else ""

    return {
        "found": False,
        "lookup_available": False,
        "identifier": identifier_str,
        "membership_no": None,
        "name": None,
        "dob": None,
        "verified": None,
        "ibc_balance": None,
        "cobrand_bank": None,
        "message": _NOT_CONNECTED_MESSAGE,
    }
