from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# HTTP request models (§4)
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    """Body of POST /api/chat."""

    session_id: Optional[str] = None
    message: str
    # Which LLM backend to use ("anthropic" | "gemini"); None = server default.
    provider: Optional[str] = None


# ---------------------------------------------------------------------------
# Session decision state (§5)
# ---------------------------------------------------------------------------


class ChecklistItem(BaseModel):
    """A single rule in the decision checklist (✅/❌/—)."""

    label: str
    ok: Optional[bool] = None


class EligibilityResult(BaseModel):
    """Last evaluate_merge_eligibility result, mirrored into SessionState."""

    decision: str
    reason_code: str
    explanation: str
    requires_program_ops_discretion: bool


class SessionState(BaseModel):
    """The decision-panel model, mirrored in frontend/src/types.ts (§5)."""

    # Coerce dicts assigned to typed fields (eligibility/checklist) into their
    # models on assignment, so model_dump() stays clean and validated.
    model_config = ConfigDict(validate_assignment=True)

    step: str = "Start"
    from_registered_email: Optional[bool] = None
    eligibility: Optional[EligibilityResult] = None
    dpa_status: Optional[Literal["pending", "passed", "failed"]] = None
    consent_primary: bool = False
    consent_other: bool = False
    escalated: bool = False
    checklist: list[ChecklistItem] = Field(default_factory=list)


def default_checklist() -> list[ChecklistItem]:
    """The "Allowed if / Not allowed if" rules, all unknown (—) at start."""
    return [
        ChecklistItem(label="Name match", ok=None),
        ChecklistItem(label="DOB match", ok=None),
        ChecklistItem(label="Both accounts verified", ok=None),
        ChecklistItem(label="Secondary has IBC balance", ok=None),
        ChecklistItem(label="Co-brand linked to primary", ok=None),
    ]


def default_session_state() -> SessionState:
    """Factory for a fresh SessionState."""
    return SessionState(checklist=default_checklist())


# ---------------------------------------------------------------------------
# SSE event payloads (§4) — typed helpers for the chat stream
# ---------------------------------------------------------------------------


class SessionEvent(BaseModel):
    """`session` event data."""

    session_id: str


class TokenEvent(BaseModel):
    """`token` event data — a chunk of assistant text."""

    text: str


class ThinkingEvent(BaseModel):
    """`thinking` event data — optional summarized thinking chunk."""

    text: str


class ToolCallEvent(BaseModel):
    """`tool_call` event data — a tool the model invoked."""

    name: str
    input: dict


class ToolResultEvent(BaseModel):
    """`tool_result` event data — that tool's result."""

    name: str
    output: dict


class DraftEvent(BaseModel):
    """`draft` event data — a generated email draft."""

    template_id: str
    subject: str
    body: str
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ErrorEvent(BaseModel):
    """`error` event data."""

    message: str


class DoneEvent(BaseModel):
    """`done` event data — end of turn."""

    session_id: str
