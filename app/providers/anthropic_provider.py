"""Anthropic Claude provider — streaming manual tool loop (CONTRACTS §2 / §4).

Drives the conversation with Claude (default Opus 4.8): adaptive thinking,
`effort` control, prompt-cached system prompt, and the shared deterministic
tools. Yields the SSE-event dicts defined in CONTRACTS §4. The Anthropic client
is constructed lazily (only when this provider is actually used) so the backend
boots without an Anthropic key when only Gemini is configured.
"""

from __future__ import annotations

import json
from typing import Any

from ..config import settings
from ..prompts.system_prompt import build_state_context, build_system_prompt
from ..tools import REGISTRY, dispatch
from .base import RENDER_GUARD_MESSAGE, BaseProvider, fallback_reply

_DRAFT_TOOL = "render_email_template"
_ELIGIBILITY_TOOL = "evaluate_merge_eligibility"
_STATE_TOOLS = frozenset({"evaluate_merge_eligibility", "record_outcome"})


def _state_payload(session: Any) -> dict:
    state = session.state
    if hasattr(state, "model_dump"):
        return state.model_dump()
    if isinstance(state, dict):
        return state
    return dict(state)


class AnthropicProvider(BaseProvider):
    id = "anthropic"
    label = "Anthropic Claude"

    def __init__(self) -> None:
        self._client = None

    def available(self) -> bool:
        return bool(settings.ANTHROPIC_API_KEY)

    def model_name(self) -> str:
        return settings.CLAUDE_MODEL

    def _get_client(self):
        if self._client is None:
            from anthropic import AsyncAnthropic

            # Resolves ANTHROPIC_API_KEY from the environment.
            self._client = AsyncAnthropic()
        return self._client

    @staticmethod
    def _messages_from_transcript(transcript: list[dict]) -> list[dict]:
        """Rebuild Anthropic messages from the neutral transcript."""
        return [{"role": t["role"], "content": t["text"]} for t in transcript]

    async def stream_turn(self, session: Any, user_message: str):
        import anthropic

        client = self._get_client()
        messages = self._messages_from_transcript(session.transcript)
        messages.append({"role": "user", "content": user_message})

        # Frozen, cached system prompt + a dynamic block carrying this session's
        # workflow state (so the model stays consistent across turns). The cached
        # block stays first/unchanged, so prompt caching still holds.
        state_ctx = build_state_context(session)
        system_blocks = build_system_prompt()
        if state_ctx:
            system_blocks = [*system_blocks, {"type": "text", "text": state_ctx}]

        assistant_text = ""
        last_draft_template: str | None = None
        any_tool_ran = False
        # Render guard: a decided eligibility with a recommended template MUST
        # produce a draft. If the model stops without one, force a render once.
        recommended_template: str | None = None
        draft_rendered = False
        render_forced = False

        try:
            while True:
                async with client.messages.stream(
                    model=settings.CLAUDE_MODEL,
                    max_tokens=settings.CLAUDE_MAX_TOKENS,
                    thinking={"type": "adaptive", "display": "summarized"},
                    output_config={"effort": settings.CLAUDE_EFFORT},
                    system=system_blocks,
                    tools=REGISTRY,
                    messages=messages,
                ) as stream:
                    async for event in stream:
                        if event.type != "content_block_delta":
                            continue
                        delta = event.delta
                        if delta.type == "text_delta":
                            assistant_text += delta.text
                            yield {"event": "token", "data": {"text": delta.text}}
                        elif delta.type == "thinking_delta":
                            yield {
                                "event": "thinking",
                                "data": {"text": delta.thinking},
                            }
                    final_message = await stream.get_final_message()

                messages.append(
                    {"role": "assistant", "content": final_message.content}
                )

                if final_message.stop_reason != "tool_use":
                    # Safety net: the model decided an eligibility that needs a
                    # specific template but stopped without drafting it. Force one
                    # render round so the draft is never silently skipped.
                    if recommended_template and not draft_rendered and not render_forced:
                        render_forced = True
                        messages.append(
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": RENDER_GUARD_MESSAGE.format(
                                            template=recommended_template
                                        ),
                                    }
                                ],
                            }
                        )
                        continue
                    # Never leave the chat empty when the model returns only tool
                    # calls / a draft with no narration.
                    if not assistant_text.strip():
                        fallback = fallback_reply(last_draft_template, any_tool_ran)
                        if fallback:
                            assistant_text += fallback
                            yield {"event": "token", "data": {"text": fallback}}
                    return

                tool_results: list[dict] = []
                for block in final_message.content:
                    if block.type != "tool_use":
                        continue

                    any_tool_ran = True
                    tool_input = block.input
                    yield {
                        "event": "tool_call",
                        "data": {"name": block.name, "input": tool_input},
                    }

                    try:
                        result = await dispatch(block.name, tool_input, session)
                    except Exception as exc:  # one tool must not kill the stream
                        result = {"error": f"{type(exc).__name__}: {exc}"}

                    # Pull any UI form directive out of the result — it is shown
                    # in the chat as a `form` event and never echoed back to the
                    # model (it only needs the rest; re-sending the spec wastes
                    # tokens). Works for any tool that returns a "form".
                    form_spec = result.pop("form", None) if isinstance(result, dict) else None

                    yield {
                        "event": "tool_result",
                        "data": {"name": block.name, "output": result},
                    }

                    if block.name == _DRAFT_TOOL:
                        last_draft_template = result.get("template_id") or last_draft_template
                        draft_rendered = True
                        yield {
                            "event": "draft",
                            "data": {
                                "template_id": result.get("template_id", ""),
                                "subject": result.get("subject", ""),
                                "body": result.get("body", ""),
                                "missing_fields": result.get("missing_fields", []),
                                "warnings": result.get("warnings", []),
                            },
                        }

                    if block.name == _ELIGIBILITY_TOOL:
                        rec = result.get("recommended_template_id")
                        if rec:
                            recommended_template = rec

                    if isinstance(form_spec, dict):
                        yield {"event": "form", "data": form_spec}

                    if block.name in _STATE_TOOLS:
                        yield {"event": "state", "data": _state_payload(session)}

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result),
                        }
                    )

                messages.append({"role": "user", "content": tool_results})

        except anthropic.APIError as exc:
            message = getattr(exc, "message", None) or str(exc)
            yield {"event": "error", "data": {"message": message}}
            return
        finally:
            # Persist the completed turn into the neutral transcript.
            session.transcript.append({"role": "user", "text": user_message})
            if assistant_text.strip():
                session.transcript.append(
                    {"role": "assistant", "text": assistant_text}
                )
