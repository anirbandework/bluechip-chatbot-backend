from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment / .env file.

    All provider API keys live only here (backend). They are never sent to the
    frontend. The app boots with zero, one, or both providers configured — a
    provider with no key is reported as unavailable and cannot be selected.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Anthropic (Claude) ---
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-opus-4-8"
    CLAUDE_MAX_TOKENS: int = 16000
    CLAUDE_EFFORT: str = "high"

    # --- Google (Gemini) ---
    # Either GEMINI_API_KEY or GOOGLE_API_KEY is accepted (the google-genai SDK
    # recognizes both); see `gemini_api_key`.
    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    # Fallback chain, tried in order on retryable errors (404/503/429/500/quota).
    # All listed models must be available to the key and support function calling.
    # flash-lite usually has a separate (larger) free-tier quota bucket, and
    # `gemini-flash-latest` is an evergreen alias used as the final fallback.
    GEMINI_MODELS: str = "gemini-2.5-flash,gemini-2.5-flash-lite,gemini-flash-latest"
    GEMINI_MAX_TOKENS: int = 8192
    # Hard per-request wall-clock cap so a hung Gemini call can't pin a worker.
    AI_CALL_TIMEOUT_SECONDS: int = 45

    # --- knowledge retrieval (RAG) ---
    # Folder of reference documents (.md/.txt/.pdf) searched by `search_knowledge`.
    # Empty -> defaults to backend/knowledge_sources. Files starting with "_" or
    # "." are ignored (e.g. _README.md).
    KNOWLEDGE_DIR: str = ""
    RETRIEVAL_TOP_K: int = 5

    # --- server ---
    # Preferred provider when the request doesn't name one (falls back to the
    # first available provider if this one has no key).
    DEFAULT_PROVIDER: str = "anthropic"
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINS as a list (comma-separated env value)."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def gemini_api_key(self) -> str:
        """The Gemini key from either accepted env var name."""
        return self.GEMINI_API_KEY or self.GOOGLE_API_KEY

    @property
    def gemini_model_list(self) -> list[str]:
        """The Gemini fallback chain as a list (comma-separated env value)."""
        return [m.strip() for m in self.GEMINI_MODELS.split(",") if m.strip()]


settings = Settings()
