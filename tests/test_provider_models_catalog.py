"""Tests for provider model catalog enrichment and fallback merge behavior."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
import asyncio
from typing import Dict, cast

from core.api_client import BaseAPIClient

from core.provider_router import ProviderRouter


def test_get_all_models_uses_fallback_when_provider_list_fails():
    router = ProviderRouter()
    failing_provider = SimpleNamespace(
        is_available=True,
        list_models=AsyncMock(side_effect=RuntimeError("boom")),
    )
    router.providers = cast(Dict[str, BaseAPIClient], {"groq": failing_provider})

    models = asyncio.run(router.get_all_models())

    assert "groq" in models
    assert isinstance(models["groq"], list)
    assert len(models["groq"]) > 3
    assert "llama-3.1-8b-instant" in models["groq"]


def test_get_all_models_prefers_live_models_when_available():
    router = ProviderRouter()
    live_provider = SimpleNamespace(
        is_available=True,
        list_models=AsyncMock(return_value=["custom-live-model", "gpt-4o"]),
    )
    router.providers = cast(Dict[str, BaseAPIClient], {"openai": live_provider})

    models = asyncio.run(router.get_all_models())

    assert "openai" in models
    # Live models preserved and deduplicated
    assert "custom-live-model" in models["openai"]
    assert models["openai"].count("gpt-4o") == 1
    # Do not force extra fallback models for available providers.
    assert "gpt-4o-mini" not in models["openai"]


def test_unavailable_provider_still_gets_fallback_catalog():
    router = ProviderRouter()
    unavailable_provider = SimpleNamespace(
        is_available=False,
        list_models=AsyncMock(return_value=[]),
    )
    router.providers = cast(Dict[str, BaseAPIClient], {"openrouter": unavailable_provider})

    models = asyncio.run(router.get_all_models())

    assert "openrouter" in models
    assert len(models["openrouter"]) > 5
    assert "openai/gpt-4o" in models["openrouter"]


def test_merge_models_preserves_order_and_strips_invalid_values():
    merged = ProviderRouter._merge_models(
        ["a", " b ", "a", "", None],
        ["b", "c", " ", "d"],
    )
    assert merged == ["a", "b", "c", "d"]
