"""Provider registry — selects an LLM backend by id.

Providers are instantiated once at import (no API client is constructed and no
key is required until a provider is actually used). ``available()`` reflects
which keys are configured, so the frontend can show/enable only usable options.
"""

from __future__ import annotations

from typing import Optional

from .anthropic_provider import AnthropicProvider
from .base import BaseProvider
from .gemini_provider import GeminiProvider

# Order here is the display order in the frontend selector.
_PROVIDERS: dict[str, BaseProvider] = {}
for _provider in (AnthropicProvider(), GeminiProvider()):
    _PROVIDERS[_provider.id] = _provider


def get_provider(provider_id: Optional[str]) -> Optional[BaseProvider]:
    """Return the provider with this id, or ``None`` if unknown."""
    if not provider_id:
        return None
    return _PROVIDERS.get(provider_id)


def list_providers() -> list[dict]:
    """Public metadata for every provider (id, label, availability, model)."""
    return [
        {
            "id": p.id,
            "label": p.label,
            "available": p.available(),
            "model": p.model_name(),
        }
        for p in _PROVIDERS.values()
    ]


def default_provider_id() -> str:
    """The preferred provider if available, else the first available one."""
    from ..config import settings

    preferred = _PROVIDERS.get(settings.DEFAULT_PROVIDER)
    if preferred is not None and preferred.available():
        return preferred.id
    for provider in _PROVIDERS.values():
        if provider.available():
            return provider.id
    # Nothing is configured — return the preferred id so the error is explicit.
    return settings.DEFAULT_PROVIDER
