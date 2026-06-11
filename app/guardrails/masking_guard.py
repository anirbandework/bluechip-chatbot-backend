"""Masking guardrail — a non-destructive last-line auditor (CONTRACTS §0, §3.3).

Primary masking is enforced **per template** by ``render_email_template`` (it
masks only the fields the SOP actually requires masked — in practice exactly one:
the OTHER account's email in T2, "Do not disclose full email ID" -> abc***@gma.com).

This module deliberately does NOT blindly scrub customer-facing text, because
several SOP emails legitimately show the recipient their OWN full credentials
(T3/T4 mobile numbers, T9 re-login email/phone). Blindly masking those would
corrupt correct emails.

Instead it AUDITS: given ``allowed_full`` — the set of credential values that are
intentionally shown in full (the non-masked field values of the rendered
template) — it flags any OTHER full email address or phone-length digit run that
appears, i.e. a credential that slipped in without going through the masking
rules. Findings are returned as human-readable warnings for the agent to review;
nothing is mutated.

The public IndiGo support numbers that appear in SOP templates are allow-listed
and never flagged. Membership numbers (9 digits) are NOT treated as phone numbers
(the phone heuristic requires >= 10 digits, the length of an Indian mobile).
"""

from __future__ import annotations

import re

from app.tools.masking import mask_email, mask_phone

# Public IndiGo BluChip support numbers that appear verbatim in the SOP templates
# (and the FAQ "+91" variants). These are NOT member credentials. Compared on
# digits only so formatting variants still match.
_PUBLIC_SUPPORT_NUMBERS: frozenset[str] = frozenset(
    {
        "01246173838",
        "01244973838",
        "911246173838",
        "911244973838",
    }
)

# Full email address. Deliberately broad but standard.
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

# A run of digits, allowing common phone separators / a leading "+" inside.
_PHONE_RE = re.compile(r"\+?\d(?:[\d\s\-]*\d)?")

# Indian member mobiles are 10 digits; 9-digit BluChip membership numbers are NOT
# phones and must not be treated as credentials.
_MIN_PHONE_DIGITS = 10


def _digits_only(text: str) -> str:
    return "".join(ch for ch in text if ch.isdigit())


def _is_public_support_number(token: str) -> bool:
    return _digits_only(token) in _PUBLIC_SUPPORT_NUMBERS


def _normalize(token: str) -> str:
    """Canonical form for comparison: lowercased email, or digits-only phone."""
    token = token.strip()
    if "@" in token:
        return token.lower()
    return _digits_only(token)


def _normalize_allowed(allowed_full: object) -> set[str]:
    out: set[str] = set()
    for value in allowed_full or ():  # type: ignore[union-attr]
        text = "" if value is None else str(value)
        if text:
            out.add(_normalize(text))
    return out


def _find_emails(text: str) -> list[str]:
    return [m.group(0) for m in _EMAIL_RE.finditer(text)]


def _find_phones(text: str) -> list[str]:
    # Remove emails first so digit runs inside an email are not mis-read as phones.
    scrubbed = _EMAIL_RE.sub(" ", text)
    found: list[str] = []
    for match in _PHONE_RE.finditer(scrubbed):
        token = match.group(0)
        if len(_digits_only(token)) >= _MIN_PHONE_DIGITS:
            found.append(token)
    return found


def find_unmasked_credentials(
    text: str, allowed_full: object = frozenset()
) -> list[str]:
    """Return credential tokens in ``text`` that are NOT intentionally disclosed.

    ``allowed_full`` is the set of credential values that are meant to appear in
    full (the rendered template's non-masked field values). Public support
    numbers are always allowed. Returns a de-duplicated list of offending tokens.
    """
    if not isinstance(text, str) or not text:
        return []

    allowed = _normalize_allowed(allowed_full)
    offending: list[str] = []
    seen: set[str] = set()

    for token in _find_emails(text):
        norm = _normalize(token)
        if norm in allowed or norm in seen:
            continue
        seen.add(norm)
        offending.append(token)

    for token in _find_phones(text):
        norm = _normalize(token)
        if norm in allowed or norm in seen or _is_public_support_number(token):
            continue
        seen.add(norm)
        offending.append(token)

    return offending


def audit_customer_text(
    text: str, allowed_full: object = frozenset()
) -> list[str]:
    """Non-mutating audit: human-readable warnings for credentials that bypassed
    masking in customer-facing text. Returns ``[]`` when the text is clean."""
    return [
        (
            f"Possible unmasked member credential in customer-facing text: "
            f"{token!r}. Verify it should be disclosed before sending."
        )
        for token in find_unmasked_credentials(text, allowed_full)
    ]


def contains_unmasked_credential(
    text: str, allowed_full: object = frozenset()
) -> bool:
    """True if ``text`` contains a credential not in ``allowed_full``."""
    return bool(find_unmasked_credentials(text, allowed_full))


def scrub_unmasked_credentials(
    text: str, allowed_full: object = frozenset()
) -> str:
    """Destructively mask credentials NOT in ``allowed_full`` (utility / tests).

    NOT used in the draft path — drafts may legitimately contain full credentials
    and are audited non-destructively via :func:`audit_customer_text`. Provided
    for defense-in-depth over arbitrary free text where nothing is intentionally
    shown in full. Never raises on odd input.
    """
    if not isinstance(text, str) or not text:
        return text

    allowed = _normalize_allowed(allowed_full)

    def _email_repl(match: re.Match[str]) -> str:
        token = match.group(0)
        return token if _normalize(token) in allowed else mask_email(token)

    text = _EMAIL_RE.sub(_email_repl, text)

    def _phone_repl(match: re.Match[str]) -> str:
        token = match.group(0)
        if len(_digits_only(token)) < _MIN_PHONE_DIGITS:
            return token
        if _is_public_support_number(token) or _normalize(token) in allowed:
            return token
        return mask_phone(token)

    return _PHONE_RE.sub(_phone_repl, text)
