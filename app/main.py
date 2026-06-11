"""FastAPI application: /api/health, /api/providers, and /api/chat (SSE).

The chat endpoint selects an LLM provider (Anthropic Claude or Google Gemini)
per request and streams that provider's tool loop as Server-Sent Events
(CONTRACTS §4). All provider API keys live only in this backend; they are never
exposed to the frontend. The deterministic SOP tools and the SSE protocol are
identical regardless of which provider is chosen.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import retrieval
from .config import settings
from .db import dispose_db, init_db
from .providers import default_provider_id, list_providers
from .routers import audit as audit_router
from .routers import auth as auth_router
from .routers import chats as chats_router
from .routers import roles as roles_router
from .routers import users as users_router
from .seed import seed


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    await seed()
    yield
    await dispose_db()


app = FastAPI(title="BluChip Agent-Assist", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(roles_router.router)
app.include_router(audit_router.router)
app.include_router(chats_router.router)


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
