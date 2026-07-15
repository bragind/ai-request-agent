from __future__ import annotations

import logging

from request_agent.config import LLMProviderName, Settings
from request_agent.providers.base import LLMProvider, ProviderError
from request_agent.providers.mock_provider import MockProvider
from request_agent.providers.ollama_provider import OllamaProvider
from request_agent.schemas import AnalyzeResponse

logger = logging.getLogger(__name__)


class RequestAnalysisService:
    def __init__(
        self,
        settings: Settings,
        provider: LLMProvider | None = None,
        fallback_provider: LLMProvider | None = None,
    ) -> None:
        self._settings = settings
        self._provider = provider or self._build_provider(settings)
        self._fallback_provider = fallback_provider or MockProvider()

    async def analyze(self, text: str) -> AnalyzeResponse:
        if self._settings.llm_provider is LLMProviderName.MOCK:
            result = await self._fallback_provider.analyze(text)
            return AnalyzeResponse(**result.model_dump(), provider="mock")

        try:
            result = await self._provider.analyze(text)
            return AnalyzeResponse(**result.model_dump(), provider="ollama")
        except ProviderError as exc:
            logger.warning("Using mock fallback because provider failed: %s", exc)
            result = await self._fallback_provider.analyze(text)
            return AnalyzeResponse(**result.model_dump(), provider="mock_fallback")

    def _build_provider(self, settings: Settings) -> LLMProvider:
        if settings.llm_provider is LLMProviderName.OLLAMA:
            return OllamaProvider(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
                timeout_seconds=settings.ollama_timeout_seconds,
            )
        return MockProvider()

