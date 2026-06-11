"""FastAPI application: /api/health, /api/providers, and /api/chat (SSE).

The chat endpoint selects an LLM provider (Anthropic Claude or Google Gemini)
per request and streams that provider's tool loop as Server-Sent Events
(CONTRACTS §4). All provider API keys live only in this backend; they are never
exposed to the frontend. The deterministic SOP tools and the SSE protocol are
identical regardless of which provider is chosen.
"""

from __future__ import annotations

import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from . import retrieval
from .config import settings
from .models import ChatRequest
from .providers import default_provider_id, get_provider, list_providers
from .sessions import store

app = FastAPI(title="BluChip Agent-Assist")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    """Liveness root (e.g. for a platform health check / hitting the base URL)."""
    return {"status": "ok", "service": "bluchip-assist-backend"}


@app.get("/api/health")
async def health() -> dict:
    """Liveness probe + configured providers."""
    return {
        "status": "ok",
        "default_provider": default_provider_id(),
        "providers": list_providers(),
    }


@app.get("/api/providers")
async def providers() -> dict:
    """Which LLM providers exist and which are configured (have a key)."""
    return {"providers": list_providers(), "default": default_provider_id()}


@app.get("/api/knowledge")
async def knowledge_stats() -> dict:
    """What's in the searchable knowledge base (files + chunk count)."""
    return retrieval.corpus_stats()


@app.post("/api/reindex")
async def reindex() -> dict:
    """Rebuild the knowledge index from disk (after adding/removing files)."""
    return retrieval.reindex()


@app.get("/api/sessions")
async def list_sessions() -> dict:
    """Past conversations (newest first) for the history sidebar."""
    return {
        "sessions": [
            {
                "id": s.id,
                "title": s.title(),
                "created_at": s.created_at,
                "message_count": sum(
                    1 for t in s.transcript if t.get("role") == "user"
                ),
            }
            for s in store.list()
        ]
    }


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str) -> dict:
    """Full history of one conversation, to restore it in the UI."""
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return {
        "id": session.id,
        "title": session.title(),
        "created_at": session.created_at,
        "transcript": session.transcript,
        "state": session.state.model_dump(),
    }


@app.post("/api/chat")
async def chat(req: ChatRequest) -> EventSourceResponse:
    """Stream a single assistant turn as SSE (CONTRACTS §4)."""
    session = store.get_or_create(req.session_id)
    provider_id = req.provider or default_provider_id()
    provider = get_provider(provider_id)

    async def event_stream():
        # Always announce the (possibly newly created) session id first.
        yield {"event": "session", "data": json.dumps({"session_id": session.id})}
        try:
            if provider is None:
                yield {
                    "event": "error",
                    "data": json.dumps(
                        {"message": f"Unknown provider: {provider_id!r}"}
                    ),
                }
            elif not provider.available():
                yield {
                    "event": "error",
                    "data": json.dumps(
                        {
                            "message": f"Provider '{provider_id}' is not configured "
                            "(missing API key)."
                        }
                    ),
                }
            else:
                async for event in provider.stream_turn(session, req.message):
                    yield {
                        "event": event["event"],
                        "data": json.dumps(event["data"]),
                    }
        except Exception as exc:  # noqa: BLE001 - surface any failure to the client
            yield {"event": "error", "data": json.dumps({"message": str(exc)})}
        finally:
            yield {"event": "done", "data": json.dumps({"session_id": session.id})}

    return EventSourceResponse(event_stream())
