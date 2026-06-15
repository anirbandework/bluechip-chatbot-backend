"""``record_outcome`` tool implementation (CONTRACTS.md section 3.5).

Appends an auditable event to the session and updates ``session.state`` so the
frontend decision panel can render progress through the merge flow.

Recognised events (CONTRACTS section 3.5)::

    call_attempt | dpa_passed | dpa_failed | consent_received
    | escalated_to_ops | resolved

Side effects on ``session.state`` (CONTRACTS section 5):

* ``dpa_passed``      -> ``dpa_status = "passed"``
* ``dpa_failed``      -> ``dpa_status = "failed"``
* ``consent_received``-> ``consent_primary`` / ``consent_other`` set ONLY from an
  explicit ``detail`` (``primary`` / ``other`` / ``secondary`` / ``both``); an
  empty or ambiguous detail sets nothing (never inferred from absence)
* ``escalated_to_ops``-> ``escalated = True``
* every event advances the human-readable ``step`` label

This module imports with no side effects.
"""

from __future__ import annotations

# Human-readable decision-panel ``step`` label per recorded event.
_STEP_LABELS: dict[str, str] = {
    "call_attempt": "Contact attempt logged",
    "dpa_passed": "DPA / verification passed",
    "dpa_failed": "DPA / verification failed",
    "consent_received": "Consent received",
    "escalated_to_ops": "Escalated to Program Ops",
    "resolved": "Resolved",
}


def _set_state(state: object, field: str, value: object) -> None:
    """Set ``field`` on ``state`` whether it is an attribute- or dict-backed model."""
    if isinstance(state, dict):
        state[field] = value
    else:
        setattr(state, field, value)


def _get_state(state: object, field: str, default: object = None) -> object:
    """Read ``field`` from ``state`` whether it is attribute- or dict-backed."""
    if isinstance(state, dict):
        return state.get(field, default)
    return getattr(state, field, default)


def _apply_consent(state: object, detail: str) -> None:
    """Update consent flags from a ``consent_received`` event's ``detail`` text.

    ``detail`` must say WHICH account consented: "primary" sets ``consent_primary``;
    "other" / "secondary" sets ``consent_other``; "both" sets both. An empty or
    ambiguous detail sets NOTHING — consent is a load-bearing audit fact and must
    never be inferred from absence (over-recording "both" could wrongly advance the
    merge). Existing True flags are never cleared.
    """
    text = (detail or "").lower()
    wants_both = "both" in text
    wants_primary = "primary" in text or wants_both
    wants_other = "other" in text or "secondary" in text or wants_both

    if wants_primary:
        _set_state(state, "consent_primary", True)
    if wants_other:
        _set_state(state, "consent_other", True)


async def record_outcome(tool_input: dict, session) -> dict:
    """Record an auditable outcome event and update the session decision state.

    Parameters
    ----------
    tool_input:
        ``{"event": "<one of the recognised events>", "detail": "<optional str>"}``.
    session:
        The current :class:`Session`; ``session.events`` is appended to and
        ``session.state`` is mutated in place.

    Returns
    -------
    dict
        ``{"recorded": True, "event": "<event>", "count": <events so far>}``
        per CONTRACTS section 3.5.
    """
    event = tool_input.get("event")
    detail = tool_input.get("detail")

    # Audit log entry — always recorded, even for unrecognised event names.
    session.events.append({"event": event, "detail": detail})

    state = session.state

    if event == "dpa_passed":
        _set_state(state, "dpa_status", "passed")
    elif event == "dpa_failed":
        _set_state(state, "dpa_status", "failed")
    elif event == "consent_received":
        _apply_consent(state, detail or "")
    elif event == "escalated_to_ops":
        _set_state(state, "escalated", True)

    # Advance the decision-panel step label for any recognised event.
    if event in _STEP_LABELS:
        _set_state(state, "step", _STEP_LABELS[event])

    return {
        "recorded": True,
        "event": event,
        "count": len(session.events),
    }
