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
from .base import (
    EMPTY_REPLY_NUDGE,
    EMPTY_TURN_FALLBACK,
    ESCALATION_GUARD_MESSAGE,
    RENDER_GUARD_MESSAGE,
    SUMMARY_SYSTEM_PROMPT,
    BaseProvider,
    fallback_reply,
)

_DRAFT_TOOL = "render_email_template"
_ELIGIBILITY_TOOL = "evaluate_merge_eligibility"
_OUTCOME_TOOL = "record_outcome"
_ESCALATE_EVENT = "escalated_to_ops"
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

    async def summarize(self, text: str) -> str:
        client = self._get_client()
        msg = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=4000,
            system=SUMMARY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
        )
        # A truncated summary would silently lose the tail; signal failure so the
        # compaction boundary does not advance.
        if getattr(msg, "stop_reason", None) == "max_tokens":
            return ""
        return "".join(
            getattr(b, "text", "")
            for b in msg.content
            if getattr(b, "type", None) == "text"
        ).strip()

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
        # Per-turn terminal-state tracking. The deterministic engine may declare a
        # required follow-up (draft a template, or escalate to Program Ops); the
        # finalizer enforces whichever is owed. At most ONE form is shown per turn
        # — the draft card wins, and an intake card is suppressed once a decision
        # or draft exists (so prose and card can never contradict).
        required_followup: dict | None = None
        draft_rendered = False
        escalation_recorded = False
        eligibility_decided = False
        guard_forced = False
        empty_retry_done = False
        draft_form: dict | None = None   # latest render's fill-in card (None if complete)
        intake_form: dict | None = None  # latest intake card

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
                    # --- Turn finalizer (deterministic terminal state) ---
                    # 1. Enforce the required follow-up the engine declared, so a
                    #    decided case always produces its draft / escalation rather
                    #    than just narration. Forced once (guard_forced) — no loop.
                    if not guard_forced and required_followup:
                        kind = required_followup.get("kind")
                        if kind == "draft" and not draft_rendered:
                            guard_forced = True
                            messages.append({
                                "role": "user",
                                "content": [{
                                    "type": "text",
                                    "text": RENDER_GUARD_MESSAGE.format(
                                        template=required_followup.get("template_id", "")
                                    ),
                                }],
                            })
                            continue
                        if kind == "escalate" and not escalation_recorded:
                            guard_forced = True
                            messages.append({
                                "role": "user",
                                "content": [{"type": "text", "text": ESCALATION_GUARD_MESSAGE}],
                            })
                            continue
                    # 1b. Empty-turn guard: the model produced NO reply (only
                    #     thinking / tool calls) and nothing to confirm. Nudge it
                    #     once to actually respond — this is the "ask again and it
                    #     works" case — rather than ending the turn blank.
                    if (
                        not assistant_text.strip()
                        and not draft_rendered
                        and not empty_retry_done
                    ):
                        empty_retry_done = True
                        messages.append({
                            "role": "user",
                            "content": [{"type": "text", "text": EMPTY_REPLY_NUDGE}],
                        })
                        continue
                    # 2. Emit AT MOST ONE form. The draft card wins; the intake card
                    #    is suppressed once a draft/decision exists (never show a
                    #    "gather more facts" card that contradicts the reply).
                    if draft_form is not None:
                        yield {"event": "form", "data": draft_form}
                    elif intake_form is not None and not draft_rendered and not eligibility_decided:
                        yield {"event": "form", "data": intake_form}
                    # 3. A turn is NEVER empty: use the model's text, else a
                    #    contextual fallback, else a guaranteed last-resort reply.
                    if not assistant_text.strip():
                        fallback = (
                            fallback_reply(last_draft_template, any_tool_ran)
                            or EMPTY_TURN_FALLBACK
                        )
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
                        # Latest render decides the fill-in card: the card when
                        # fields are still missing, or None once the draft is
                        # complete (so a complete re-render clears a stale card).
                        draft_form = form_spec if isinstance(form_spec, dict) else None
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
                    elif isinstance(form_spec, dict):
                        # Any other tool that returns a form (request_intake_form).
                        intake_form = form_spec

                    if block.name == _ELIGIBILITY_TOOL:
                        eligibility_decided = True
                        followup = result.get("required_followup")
                        if isinstance(followup, dict):
                            required_followup = followup

                    if (
                        block.name == _OUTCOME_TOOL
                        and isinstance(tool_input, dict)
                        and tool_input.get("event") == _ESCALATE_EVENT
                    ):
                        escalation_recorded = True

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
