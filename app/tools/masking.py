"""Credential masking helpers (CONTRACTS §3.2).

These functions produce the customer-facing masked form of a member's email
or phone number. The SOP rule is: only the first 3 letters of an email and the
last 3 digits of a phone number may be disclosed to a customer.

Both functions are defensive: short or garbage input must never raise and must
never reveal more than the rule allows. When in doubt, mask more, not less.

Target shapes:
    mask_email("abcdef@gmail.com") -> "abc***@gma***.com"
    mask_phone("9876543210")       -> "*******210"
"""

from __future__ import annotations


def mask_email(value: str) -> str:
    """Mask an email address for customer-facing disclosure.

    Keeps the first 3 chars of the local part, then ``***@``, then the first 3
    chars of the domain label, then ``***.`` + the top-level domain.
    Example: ``abcdef@gmail.com`` -> ``abc***@gma***.com``.

    Defensive behavior:
    - Non-string / empty input -> ``"***"``.
    - Missing ``@`` -> treat the whole thing as a local part and mask it.
    - Local part or domain label shorter than 3 chars -> disclose only what is
      available (never pad, never reveal beyond what exists).
    """
    if not isinstance(value, str):
        return "***"
    value = value.strip()
    if not value:
        return "***"

    # No "@" at all: mask as if it were a bare local part.
    if "@" not in value:
        return _mask_label(value) + "***"

    local, _, domain = value.partition("@")
    masked_local = _mask_label(local) + "***"

    domain = domain.strip()
    if not domain:
        # Trailing "@" with nothing after it.
        return masked_local + "@***"

    # Split the domain into its label and the remaining suffix (".com" etc.).
    # The first label is partially disclosed; the TLD (last segment) is kept.
    parts = domain.split(".")
    first_label = parts[0]
    masked_domain = _mask_label(first_label) + "***"

    if len(parts) >= 2:
        tld = parts[-1]
        masked_domain += "." + tld
    # If there is no dot in the domain there is no TLD to append.

    return f"{masked_local}@{masked_domain}"


def mask_phone(value: str) -> str:
    """Mask a phone number, keeping only the LAST 3 digits.

    Every digit except the final 3 is replaced with ``*``; the length of the
    digit run is preserved. Non-digit characters in the input are dropped so the
    result is a clean masked digit run.
    Example: ``9876543210`` -> ``*******210``; ``+91 98765 43210`` -> masked
    over the 12 digits.

    Defensive behavior:
    - Non-string input -> ``"***"``.
    - No digits at all -> ``"***"``.
    - 3 or fewer digits -> fully masked (never disclose the whole number when it
      is too short for the rule to leave anything hidden).
    """
    if not isinstance(value, str):
        return "***"

    digits = [c for c in value if c.isdigit()]
    if not digits:
        return "***"

    n = len(digits)
    if n <= 3:
        # Too short to safely reveal the last 3 without revealing everything.
        return "*" * n

    visible = "".join(digits[-3:])
    return ("*" * (n - 3)) + visible


def _mask_label(label: str) -> str:
    """Return at most the first 3 chars of ``label`` (defensive helper)."""
    if not isinstance(label, str):
        return ""
    label = label.strip()
    return label[:3]
