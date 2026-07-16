from __future__ import annotations

from typing import Protocol

from request_agent.schemas import LLMResult

# Общий интерфейс позволяет сервису одинаково вызывать Ollama и mock-реализацию.


class ProviderError(RuntimeError):
    """Обозначает контролируемый сбой провайдера, допускающий fallback."""

    pass


class LLMProvider(Protocol):
    """Фиксирует единый контракт реального и имитационного провайдеров."""

    async def analyze(self, text: str) -> LLMResult:
        """Анализирует нормализованный текст и возвращает проверяемый результат."""

        raise NotImplementedError
