from __future__ import annotations

import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict

# Process-stable fallback JWT secret for local dev when JWT_SECRET is unset.
# In production JWT_SECRET MUST be set, or tokens are invalidated on every restart.
_EPHEMERAL_JWT_SECRET = secrets.token_urlsafe(48)


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
    # Public origin of the frontend, used to build invite / password-reset links.
    FRONTEND_URL: str = "http://localhost:5173"

    # --- database ---
    # Default is a local SQLite file for dev; set to the Railway/Azure Postgres
    # URL in production (postgresql://… is auto-rewritten to the async driver).
    DATABASE_URL: str = "sqlite+aiosqlite:///./dev.db"

    # --- auth / security ---
    JWT_SECRET: str = ""  # REQUIRED in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_TTL_MINUTES: int = 30
    REFRESH_TOKEN_TTL_DAYS: int = 14
    INVITE_TOKEN_TTL_HOURS: int = 72
    RESET_TOKEN_TTL_HOURS: int = 2
    LOGIN_RATE_WINDOW_SECONDS: int = 300

    # --- first-run bootstrap superadmin (created only if the users table is empty) ---
    SUPERADMIN_EMAIL: str = ""
    SUPERADMIN_PASSWORD: str = ""
    SUPERADMIN_NAME: str = "Super Admin"

    # --- email (SMTP) — optional. If unset, invite/reset links are surfaced to
    # admins to share manually instead of being emailed. ---
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_STARTTLS: bool = True

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

    @property
    def sqlalchemy_url(self) -> str:
        """DATABASE_URL normalized to an async SQLAlchemy driver URL."""
        url = self.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            url = "postgresql+asyncpg://" + url[len("postgres://") :]
        elif url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://") :]
        return url

    @property
    def jwt_secret(self) -> str:
        """The signing secret (a stable ephemeral one in dev if JWT_SECRET unset)."""
        return self.JWT_SECRET or _EPHEMERAL_JWT_SECRET

    @property
    def email_enabled(self) -> bool:
        """True when SMTP is configured well enough to send mail."""
        return bool(self.SMTP_HOST and self.SMTP_FROM)


settings = Settings()
