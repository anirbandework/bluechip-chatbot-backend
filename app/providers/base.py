"""Provider interface — one LLM backend behind a uniform streaming contract.

Each provider turns a user message into the same stream of SSE-event dicts
(``{"event": <type>, "data": <dict>}``) defined in CONTRACTS §4, using the same
deterministic tools (``app.tools.REGISTRY`` / ``dispatch``). Only the underlying
LLM orchestration differs (Anthropic Messages API vs Google Gemini
generate_content). The provider is selected per request; the deterministic
workflow logic and SSE protocol are identical across providers.
"""

from __future__ import annotations

from typing import Any, AsyncGenerator

# System prompt for compacting a long chat into a running summary (see
# services.chats.compact_session). The deterministic workflow state is preserved
# separately, so this captures the conversational narrative + any loose facts.
SUMMARY_SYSTEM_PROMPT = (
    "You are compacting a BluChip Agent-Assist support conversation so it fits "
    "the model's context window. Write a CONCISE but COMPLETE summary that "
    "preserves everything needed to continue the case without the original "
    "messages: the member's situation and any identity facts given; every fact "
    "gathered (name match, DOB match, verification/DPA, IBC balance, co-brand "
    "linkage, which mobile is Primary); each eligibility decision and its reason; "
    "every email drafted (named by its plain-English purpose) and the field "
    "values used; outcomes recorded; and any pending next action. Use tight "
    "bullet points grouped by topic. Do NOT invent anything or add commentary. "
    "Output only the summary."
)

# Injected as a synthetic user turn when the model decided an eligibility that
# requires a specific email template but ended the turn without drafting it.
# Forces the provider's tool loop to run one more round so the draft is produced
# (see each provider's render guard). ``{template}`` is the recommended id.
RENDER_GUARD_MESSAGE = (
    "SYSTEM: You decided the eligibility but did NOT draft the required email. "
    'This outcome needs the email template "{template}". You MUST now call '
    'render_email_template with template_id="{template}" and whatever fields you '
    "already have (omit any you don't know — they become a fill-in card for the "
    "agent). After it renders, give the agent a short plain-language summary of "
    "the decision and that the draft is ready. Do not reply without rendering."
)

# Injected when the eligibility outcome is CONDITIONAL / requires Program Ops
# discretion (e.g. a date-of-birth mismatch) but the model ended the turn without
# recording the escalation. Forces the audit-trail event so the decision panel
# and history reflect the escalation deterministically.
ESCALATION_GUARD_MESSAGE = (
    "SYSTEM: This outcome is CONDITIONAL and requires Program Ops discretion "
    "(e.g. a date-of-birth mismatch), but you did NOT record the escalation. You "
    'MUST now call record_outcome with event="escalated_to_ops" and a short '
    "detail of why. Do NOT draft a customer denial or approval — this needs a "
    "human Program Ops decision. Then tell the agent in plain language that the "
    "case is escalated to Program Ops. Do not reply without recording it."
)


# Injected when the model ends a turn with NO reply at all (only thinking / tool
# calls). Forces one more round so the agent gets a real answer — the "ask again
# and it works" case — instead of a blank turn.
EMPTY_REPLY_NUDGE = (
    "SYSTEM: You ended your turn without any reply to the agent. Respond NOW in "
    "plain language — answer the question, or summarize the outcome and the next "
    "step. If you meant to use a tool, call it. Never return an empty turn."
)

# Last-resort reply so a turn is NEVER empty, even if the nudge also produced
# nothing. Guarantees the UI always shows a response.
EMPTY_TURN_FALLBACK = (
    "Sorry — I didn't manage to put together a response just now. Please resend "
    "your message or add a little more detail and I'll help."
)


def fallback_reply(draft_template: str | None, any_tool_ran: bool) -> str:
    """A short stand-in reply for turns that produced only tool calls / a draft
    with no narration — so the chat is never left empty. Returns ``""`` when
    nothing happened (the caller then adds no message)."""
    if draft_template:
        from ..knowledge.email_templates import template_label

        name = template_label(draft_template)
        # No raw template code in user-facing text (HARD INVARIANT #6).
        return (
            f"I've drafted the **{name}** email — open the **Email Draft** panel "
            "on the right to review, edit, and copy it."
        )
    if any_tool_ran:
        return "Done — let me know if you'd like anything else."
    return ""


class BaseProvider:
    """Base class for an LLM provider."""

    id: str = ""
    label: str = ""

    def available(self) -> bool:
        """True when this provider is configured (its API key is present)."""
        raise NotImplementedError

    def model_name(self) -> str:
        """The primary model id this provider will use."""
        raise NotImplementedError

    async def stream_turn(
        self, session: Any, user_message: str
    ) -> AsyncGenerator[dict, None]:
        """Run one assistant turn, yielding SSE-event dicts (CONTRACTS §4).

        Implementations append the user message and the final assistant text to
        ``session.transcript`` so the next turn (and the other provider) sees the
        conversation.
        """
        raise NotImplementedError
        yield  # pragma: no cover - marks this as an async generator

    async def summarize(self, text: str) -> str:
        """Return a concise summary of ``text`` (used to compact long chats).

        Default raises; each provider implements a one-shot, non-streaming call.
        """
        raise NotImplementedError
