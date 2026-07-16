from __future__ import annotations

import logging

from request_agent.config import LLMProviderName, Settings
from request_agent.providers.base import LLMProvider, ProviderError
from request_agent.providers.mock_provider import MockProvider
from request_agent.providers.ollama_provider import OllamaProvider
from request_agent.schemas import AnalyzeResponse

# Сервисный слой объединяет точки входа и скрывает от них устройство провайдеров.

logger = logging.getLogger(__name__)


class RequestAnalysisService:
    """Оркестрирует провайдеры и переключается на mock при сбое Ollama."""

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
        """Возвращает единый ответ с отметкой фактически выбранного режима."""

        # В mock-режиме тот же резервный провайдер используется как основной.
        # В Ollama-режиме метка mock_fallback позволяет отличить штатный mock
        # от автоматического восстановления после контролируемой ошибки модели.
        if self._settings.llm_provider is LLMProviderName.MOCK:
            result = await self._fallback_provider.analyze(text)
            return AnalyzeResponse(**result.model_dump(), provider="mock")

        try:
            result = await self._provider.analyze(text)
            return AnalyzeResponse(**result.model_dump(), provider="ollama")
        # Fallback сохраняет доступность локального прототипа при ожидаемом сбое
        # Ollama, не смешивая сетевую обработку с детерминированными правилами.
        except ProviderError as exc:
            logger.warning("Using mock fallback because provider failed: %s", exc)
            result = await self._fallback_provider.analyze(text)
            return AnalyzeResponse(**result.model_dump(), provider="mock_fallback")

    def _build_provider(self, settings: Settings) -> LLMProvider:
        """Создаёт провайдер согласно конфигурации, сохраняя общий контракт."""

        if settings.llm_provider is LLMProviderName.OLLAMA:
            return OllamaProvider(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
                timeout_seconds=settings.ollama_timeout_seconds,
            )
        return MockProvider()
