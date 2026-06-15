"""``render_email_template`` tool implementation (CONTRACTS.md §3.3).

Renders one of the SOP templates (``T1``..``T10``), substituting ``{field}``
placeholders from the supplied ``fields`` mapping.

Masking is **per template**, faithful to the SOP. Each template may declare a
``mask_fields`` list naming the fields that must be masked because they
cross-disclose a member credential to a *different* party. In practice the SOP
masks exactly one thing: the OTHER account's email in **T2** ("Do not disclose
full email ID" -> ``abc***@gma.com``). A template with no ``mask_fields`` shows
all its fields in full, because the remaining emails/mobiles are shown to the
*verified owner* of that account (T3/T4 mobiles, T9 re-login email/phone) or are
internal (T10).

After rendering a customer-facing template, a non-destructive guardrail audit
(:mod:`app.guardrails.masking_guard`) checks the subject/body for any credential
that bypassed masking and surfaces it in ``warnings`` for the agent to review —
it never mutates the legitimately-full values.

Unfilled ``{placeholder}`` tokens are never silently blanked: they are reported
in ``missing_fields`` and a ``[MISSING: field]`` token is left in the text.

This module imports with no side effects.
"""

from __future__ import annotations

import re

from app.guardrails import masking_guard
from app.knowledge.email_templates import TEMPLATES
from app.tools import masking

# Matches a single ``{snake_case_field}`` placeholder.
_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def _mask_value(name: str, value: str) -> str:
    """Mask a value flagged for masking, choosing email vs phone by name/shape.

    A flagged field is never returned in full: if it cannot be classified as a
    phone it is masked as an email (the more conservative redaction).
    """
    text = "" if value is None else str(value)
    if name.endswith("_email") or "@" in text:
        return masking.mask_email(text)
    stripped = text.replace(" ", "").replace("-", "").replace("+", "")
    if name.endswith("_phone") or stripped.isdigit():
        return masking.mask_phone(text)
    return masking.mask_email(text)


def _render_text(
    text: str,
    fields: dict,
    mask_fields: set[str],
    missing_fields: list[str],
) -> str:
    """Substitute ``{placeholder}`` tokens, masking only fields in ``mask_fields``.

    Each distinct unfilled placeholder is recorded once (in encounter order) in
    ``missing_fields`` and replaced with a ``[MISSING: name]`` token.
    """

    def _replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in fields and fields[name] is not None and str(fields[name]) != "":
            value = str(fields[name])
            return _mask_value(name, value) if name in mask_fields else value
        if name not in missing_fields:
            missing_fields.append(name)
        return f"[MISSING: {name}]"

    return _PLACEHOLDER_RE.sub(_replace, text)


async def render_email_template(tool_input: dict, session) -> dict:
    """Render an SOP email template, masking only the SOP-required field(s).

    Parameters
    ----------
    tool_input:
        ``{"template_id": "T1..T10", "fields": {"<name>": "<str>", ...}}``.
    session:
        The current :class:`Session` (unused; kept for the uniform tool
        dispatch signature).

    Returns
    -------
    dict
        ``{"template_id", "subject", "body", "missing_fields", "warnings"}`` per
        CONTRACTS §3.3. Unknown ``template_id`` yields an ``error`` key.
    """
    template_id = tool_input.get("template_id")
    fields = tool_input.get("fields") or {}
    if not isinstance(fields, dict):
        fields = {}

    template = TEMPLATES.get(template_id) if template_id else None
    if template is None:
        return {
            "template_id": template_id,
            "subject": "",
            "body": "",
            "missing_fields": [],
            "warnings": [],
            "error": (
                f"Unknown template_id: {template_id!r}. Valid ids are "
                f"{', '.join(sorted(TEMPLATES))}."
            ),
        }

    mask_fields = set(template.get("mask_fields", []))

    missing_fields: list[str] = []
    subject = _render_text(
        template.get("subject", ""), fields, mask_fields, missing_fields
    )
    body = _render_text(
        template.get("body", ""), fields, mask_fields, missing_fields
    )

    # Non-destructive privacy audit for customer-facing templates. The internal
    # Program Ops template (T10) may carry full credentials and is not audited.
    warnings: list[str] = []
    if template.get("audience") != "internal":
        allowed_full = {
            str(value)
            for name, value in fields.items()
            if name not in mask_fields and value is not None and str(value) != ""
        }
        seen: set[str] = set()
        for warning in masking_guard.audit_customer_text(
            body, allowed_full
        ) + masking_guard.audit_customer_text(subject, allowed_full):
            if warning not in seen:
                seen.add(warning)
                warnings.append(warning)

    result = {
        "template_id": template_id,
        "subject": subject,
        "body": body,
        "missing_fields": missing_fields,
        "warnings": warnings,
    }

    # Surface any unfilled placeholders as an interactive "complete the draft"
    # card (the provider emits result["form"] as a `form` SSE event and strips
    # it from what the model sees).
    if missing_fields:
        from app.tools.forms import build_fields_form

        form = build_fields_form(template_id, missing_fields)
        if form is not None:
            result["form"] = form

    return result
