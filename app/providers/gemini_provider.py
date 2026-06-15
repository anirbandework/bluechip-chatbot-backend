"""Google Gemini provider — streaming function-calling loop (CONTRACTS §4).

Mirrors the Anthropic provider's behavior using the google-genai SDK: it streams
tokens, lets the model call the SAME deterministic tools (`app.tools.REGISTRY` /
`dispatch`), and yields the same SSE events. The deterministic SOP logic, masking
and the SSE protocol are identical to the Anthropic path.

Adapted from a shared-client pattern with **automatic model fallback**: a
singleton client (reading `GEMINI_API_KEY` or `GOOGLE_API_KEY`), a fallback chain
of models tried in order on retryable errors (503/429/500/quota/unavailable), and
a hard per-request wall-clock timeout on the client so a hung call can't pin a
worker. The fallback only kicks in *before* any token of a round has been
emitted; a failure after streaming has begun is surfaced as an `error` event
rather than silently restarting mid-message.
"""

from __future__ import annotations

import inspect
import json
import re
from typing import Any

from ..config import settings
from ..prompts.system_prompt import build_state_context, build_system_text
from ..tools import REGISTRY, dispatch
from .base import RENDER_GUARD_MESSAGE, BaseProvider, fallback_reply

try:
    from google import genai
    from google.genai import types

    _GENAI_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when SDK is absent
    genai = None  # type: ignore[assignment]
    types = None  # type: ignore[assignment]
    _GENAI_AVAILABLE = False

_DRAFT_TOOL = "render_email_template"
_ELIGIBILITY_TOOL = "evaluate_merge_eligibility"
_STATE_TOOLS = frozenset({"evaluate_merge_eligibility", "record_outcome"})

# HTTP status codes worth retrying on the next model in the chain. 404 is
# included so a model that is unavailable for this key/API version is skipped
# to the next model rather than surfacing a hard error.
_RETRYABLE_CODES = {404, 408, 409, 429, 500, 502, 503, 504, 529}
_RETRYABLE_KEYWORDS = (
    "404", "not_found", "not found", "not supported", "no longer available",
    "503", "unavailable", "overloaded", "high demand",
    "429", "resource_exhausted", "quota",
    "500", "internal", "502", "504",
    "deadline", "timeout",
)


def _is_retryable(error: Exception) -> bool:
    """Whether to fall back to the next model in the chain."""
    code = getattr(error, "code", None) or getattr(error, "status_code", None)
    if isinstance(code, int) and code in _RETRYABLE_CODES:
        return True
    text = str(error).lower()
    return any(keyword in text for keyword in _RETRYABLE_KEYWORDS)


def _code(error: Exception):
    return getattr(error, "code", None) or getattr(error, "status_code", None)


def _describe_error(error: Exception) -> str:
    """A one-line, human-friendly summary of a Gemini exception."""
    code = _code(error)
    raw = getattr(error, "message", None) or str(error) or repr(error)
    first = str(raw).strip().split("\n")[0]
    low = first.lower()
    if code == 429 or "resource_exhausted" in low or "quota" in low:
        retry = re.search(r"retry in ([\d.]+)s", str(raw))
        hint = f" Retry in ~{int(float(retry.group(1))) + 1}s." if retry else ""
        return f"rate limit / quota exceeded (HTTP 429).{hint}"
    if code == 503 or "unavailable" in low or "high demand" in low:
        return "temporarily overloaded (HTTP 503) — try again shortly."
    if code == 404 or "not_found" in low or "not found" in low:
        return "not available for this key (HTTP 404)."
    return (f"[{code}] " if code else "") + first[:200]


def _combined_error(errors: list) -> str:
    """Summarize why every model in the chain failed, with an actionable hint."""
    details = "; ".join(f"{model}: {_describe_error(exc)}" for model, exc in errors)
    is_quota = any(
        _code(exc) == 429
        or "quota" in str(getattr(exc, "message", None) or exc).lower()
        for _, exc in errors
    )
    if is_quota:
        head = (
            "All available Gemini models are rate-limited / out of free-tier "
            "quota — this is a Gemini API key limit, not an app error. "
        )
    else:
        head = "All Gemini models failed. "
    tail = (
        " Wait for the quota to reset and retry, switch the provider in the Model "
        "dropdown, or use a key with higher quota / billing enabled."
    )
    return head + details + tail


def _state_payload(session: Any) -> dict:
    state = session.state
    if hasattr(state, "model_dump"):
        return state.model_dump()
    if isinstance(state, dict):
        return state
    return dict(state)


def _parts(chunk: Any) -> list:
    """Flatten the content parts across all candidates of a stream chunk."""
    out: list = []
    for candidate in (getattr(chunk, "candidates", None) or []):
        content = getattr(candidate, "content", None)
        if content and getattr(content, "parts", None):
            out.extend(content.parts)
    return out


# Gemini's function-declaration schema does NOT accept JSON-Schema open maps
# (`additionalProperties`) — the API rejects them with 400 INVALID_ARGUMENT
# ("Unknown name 'additional_properties'"). We rewrite any open-map object
# parameter into a STRING holding a JSON object, then parse it back before
# dispatch so the shared tools/dispatch stay provider-agnostic.
_JSON_OBJECT_HINT = (
    'Provide a JSON object string mapping placeholder names to values, '
    'e.g. {"member_last_name": "Rao", "agent_name": "Asha"}.'
)


def _is_open_map(node: Any) -> bool:
    return (
        isinstance(node, dict)
        and node.get("type") == "object"
        and "additionalProperties" in node
        and not node.get("properties")
    )


def _clean_schema(node: Any) -> Any:
    """Return a Gemini-safe copy of a JSON-schema node.

    Strips `additionalProperties` (unsupported by the Gemini API) everywhere and
    rewrites any open-map object into a STRING carrying a JSON-object hint.
    """
    if not isinstance(node, dict):
        return node
    if _is_open_map(node):
        desc = (node.get("description", "") + " " + _JSON_OBJECT_HINT).strip()
        return {"type": "string", "description": desc}
    out: dict = {}
    for key, value in node.items():
        if key == "additionalProperties":
            continue
        if key == "properties" and isinstance(value, dict):
            out[key] = {k: _clean_schema(v) for k, v in value.items()}
        elif key == "items":
            out[key] = _clean_schema(value)
        elif key in ("anyOf", "allOf", "oneOf") and isinstance(value, list):
            out[key] = [_clean_schema(v) for v in value]
        else:
            out[key] = value
    return out


def _json_string_params(input_schema: dict) -> set[str]:
    """Top-level parameter names that were rewritten to JSON strings (open maps)."""
    props = (input_schema or {}).get("properties", {}) or {}
    return {name for name, sub in props.items() if _is_open_map(sub)}


class GeminiProvider(BaseProvider):
    id = "gemini"
    label = "Google Gemini"

    def __init__(self) -> None:
        self._client = None
        self._tools = None
        self._json_fields: dict[str, set[str]] = {}

    def available(self) -> bool:
        return _GENAI_AVAILABLE and bool(settings.gemini_api_key)

    def model_name(self) -> str:
        models = settings.gemini_model_list
        return models[0] if models else "gemini-2.5-flash"

    # -- lazy singletons ----------------------------------------------------

    def _get_client(self):
        if self._client is None:
            key = settings.gemini_api_key
            http_options = None
            try:
                http_options = types.HttpOptions(
                    timeout=settings.AI_CALL_TIMEOUT_SECONDS * 1000  # ms
                )
            except Exception:
                http_options = None
            self._client = (
                genai.Client(api_key=key, http_options=http_options)
                if http_options is not None
                else genai.Client(api_key=key)
            )
        return self._client

    def _get_tools(self) -> list:
        if self._tools is None:
            self._tools = [
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=t["name"],
                            description=t["description"],
                            parameters=_clean_schema(t["input_schema"]),
                        )
                        for t in REGISTRY
                    ]
                )
            ]
            self._json_fields = {
                t["name"]: _json_string_params(t["input_schema"]) for t in REGISTRY
            }
        return self._tools

    def _adapt_args(self, name: str, args: dict) -> dict:
        """Parse any JSON-string params (rewritten open maps) back into dicts."""
        json_fields = self._json_fields.get(name)
        if not json_fields:
            return args
        adapted = dict(args)
        for field in json_fields:
            value = adapted.get(field)
            if isinstance(value, str):
                try:
                    adapted[field] = json.loads(value)
                except (ValueError, TypeError):
                    pass  # leave as-is; dispatch handles a non-dict gracefully
        return adapted

    def _config(self, extra_system: str | None = None):
        system = build_system_text()
        if extra_system:
            system = f"{system}\n\n{extra_system}"
        return types.GenerateContentConfig(
            system_instruction=system,
            tools=self._get_tools(),
            # We handle tool calls ourselves; never auto-execute.
            automatic_function_calling={"disable": True},
            max_output_tokens=settings.GEMINI_MAX_TOKENS,
            temperature=0,
        )

    @staticmethod
    def _contents_from_transcript(transcript: list[dict]) -> list:
        return [
            types.Content(
                role="model" if t["role"] == "assistant" else "user",
                parts=[types.Part.from_text(text=t["text"])],
            )
            for t in transcript
        ]

    # -- main loop ----------------------------------------------------------

    async def stream_turn(self, session: Any, user_message: str):
        if not self.available():
            yield {
                "event": "error",
                "data": {
                    "message": "Gemini is not configured "
                    "(set GEMINI_API_KEY or GOOGLE_API_KEY)."
                },
            }
            return

        client = self._get_client()
        config = self._config(build_state_context(session))
        models = settings.gemini_model_list or [self.model_name()]

        contents = self._contents_from_transcript(session.transcript)
        contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
        )

        assistant_text_total = ""
        model_idx = 0  # current working model; sticks once a round succeeds
        last_draft_template: str | None = None
        any_tool_ran = False
        # Render guard (see base.RENDER_GUARD_MESSAGE).
        recommended_template: str | None = None
        draft_rendered = False
        render_forced = False

        try:
            while True:
                round_text = ""
                fn_calls: list = []
                fn_sigs: list = []
                ri = model_idx
                round_done = False
                round_errors: list = []

                while ri < len(models):
                    model = models[ri]
                    round_text = ""
                    fn_calls = []
                    fn_sigs = []
                    emitted = False
                    try:
                        stream = client.aio.models.generate_content_stream(
                            model=model, contents=contents, config=config
                        )
                        if inspect.isawaitable(stream):
                            stream = await stream
                        async for chunk in stream:
                            for part in _parts(chunk):
                                text = getattr(part, "text", None)
                                if text:
                                    round_text += text
                                    emitted = True
                                    yield {"event": "token", "data": {"text": text}}
                                fc = getattr(part, "function_call", None)
                                if fc:
                                    fn_calls.append(fc)
                                    # Preserve the thinking-model signature so the
                                    # functionCall part can be echoed back: newer
                                    # Gemini models REQUIRE it on the returned turn.
                                    fn_sigs.append(
                                        getattr(part, "thought_signature", None)
                                    )
                        model_idx = ri  # stick with this working model
                        round_done = True
                        break
                    except Exception as exc:  # noqa: BLE001
                        round_errors.append((model, exc))
                        if not emitted and _is_retryable(exc) and ri < len(models) - 1:
                            ri += 1
                            continue
                        if emitted:
                            yield {
                                "event": "error",
                                "data": {
                                    "message": f"Gemini ({model}) failed mid-stream: "
                                    f"{_describe_error(exc)}"
                                },
                            }
                        else:
                            yield {
                                "event": "error",
                                "data": {"message": _combined_error(round_errors)},
                            }
                        return

                if not round_done:
                    yield {
                        "event": "error",
                        "data": {"message": _combined_error(round_errors)},
                    }
                    return

                assistant_text_total += round_text

                # Record the model turn (text + any function-call parts).
                model_parts: list = []
                if round_text:
                    model_parts.append(types.Part.from_text(text=round_text))
                for fc, sig in zip(fn_calls, fn_sigs):
                    model_parts.append(
                        types.Part(function_call=fc, thought_signature=sig)
                        if sig is not None
                        else types.Part(function_call=fc)
                    )
                if model_parts:
                    contents.append(types.Content(role="model", parts=model_parts))

                if not fn_calls:
                    # Safety net: decided an eligibility that needs a template but
                    # stopped without drafting it — force one render round.
                    if recommended_template and not draft_rendered and not render_forced:
                        render_forced = True
                        contents.append(
                            types.Content(
                                role="user",
                                parts=[
                                    types.Part.from_text(
                                        text=RENDER_GUARD_MESSAGE.format(
                                            template=recommended_template
                                        )
                                    )
                                ],
                            )
                        )
                        continue
                    # Some turns end with only tool calls and no narration. Never
                    # leave the chat empty — add a short reply (also saved to the
                    # transcript via assistant_text_total).
                    if not assistant_text_total.strip():
                        fallback = fallback_reply(last_draft_template, any_tool_ran)
                        if fallback:
                            assistant_text_total += fallback
                            yield {"event": "token", "data": {"text": fallback}}
                    return  # turn complete

                # Execute every function call and feed responses back.
                response_parts: list = []
                for fc in fn_calls:
                    name = fc.name
                    any_tool_ran = True
                    args = self._adapt_args(name, dict(fc.args) if fc.args else {})
                    yield {"event": "tool_call", "data": {"name": name, "input": args}}

                    try:
                        result = await dispatch(name, args, session)
                    except Exception as exc:  # one tool must not kill the stream
                        result = {"error": f"{type(exc).__name__}: {exc}"}

                    # Pull any UI form directive out of the result — shown in the
                    # chat as a `form` event, never echoed back to the model.
                    form_spec = result.pop("form", None) if isinstance(result, dict) else None

                    yield {
                        "event": "tool_result",
                        "data": {"name": name, "output": result},
                    }

                    if name == _DRAFT_TOOL:
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

                    if name == _ELIGIBILITY_TOOL:
                        rec = result.get("recommended_template_id")
                        if rec:
                            recommended_template = rec

                    if isinstance(form_spec, dict):
                        yield {"event": "form", "data": form_spec}

                    if name in _STATE_TOOLS:
                        yield {"event": "state", "data": _state_payload(session)}

                    response_parts.append(
                        types.Part.from_function_response(
                            name=name,
                            response=result if isinstance(result, dict) else {"result": result},
                        )
                    )

                contents.append(types.Content(role="user", parts=response_parts))

        finally:
            session.transcript.append({"role": "user", "text": user_message})
            if assistant_text_total.strip():
                session.transcript.append(
                    {"role": "assistant", "text": assistant_text_total}
                )
