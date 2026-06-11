# bluechip-chatbot-backend

FastAPI backend for the **IndiGo BluChip Agent-Assist** chatbot — deterministic
merge-account tools + BM25 retrieval over [`knowledge_sources/`](knowledge_sources),
dual LLM providers (Gemini / Anthropic), SSE streaming. Drafts emails & routes to
Program Ops; it never sends or approves.

> Contains IndiGo internal SOP / T&C / FAQ content in `knowledge_sources/` —
> keep this repository **private**.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload     # http://localhost:8000
```

## Deploy (Docker — Railway / Azure Container Apps / Fly / …)
This repo is the build context; it ships a portable [`Dockerfile`](Dockerfile).
The host injects `$PORT`. Set these env vars on the platform (`.env` is git-ignored):

| Key | Notes |
|-----|-------|
| `GEMINI_API_KEY` | Google AI Studio key (or use Anthropic) |
| `ANTHROPIC_API_KEY` | optional |
| `DEFAULT_PROVIDER` | `gemini` or `anthropic` |
| `CORS_ORIGINS` | the frontend origin(s), comma-separated |
