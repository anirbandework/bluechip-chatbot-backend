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


def fallback_reply(draft_template: str | None, any_tool_ran: bool) -> str:
    """A short stand-in reply for turns that produced only tool calls / a draft
    with no narration — so the chat is never left empty. Returns ``""`` when
    nothing happened (the caller then adds no message)."""
    if draft_template:
        from ..knowledge.email_templates import template_label

        name = template_label(draft_template)
        return (
            f"I've drafted the **{name}** email ({draft_template}) — open the "
            "**Email Draft** panel on the right to review, edit, and send it."
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
