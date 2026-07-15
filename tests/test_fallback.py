from __future__ import annotations

from request_agent.config import LLMProviderName, Settings
from request_agent.providers.base import ProviderError
from request_agent.schemas import LLMResult, Priority, RequestType
from request_agent.service import RequestAnalysisService


class FailingProvider:
    async def analyze(self, text: str) -> LLMResult:
        raise ProviderError("boom")


class StaticProvider:
    async def analyze(self, text: str) -> LLMResult:
        return LLMResult(
            request_type=RequestType.CONSULTATION,
            summary="Пользователь просит консультацию.",
            priority=Priority.MEDIUM,
            needs_human=False,
            confidence=0.9,
        )


async def test_unavailable_ollama_uses_mock_fallback() -> None:
    service = RequestAnalysisService(
        Settings(llm_provider=LLMProviderName.OLLAMA),
        provider=FailingProvider(),
    )
    result = await service.analyze("Не могу войти в личный кабинет, срочно.")
    assert result.provider == "mock_fallback"
    assert result.request_type == RequestType.ACCOUNT_ACCESS


async def test_valid_ollama_provider_result_is_used() -> None:
    service = RequestAnalysisService(
        Settings(llm_provider=LLMProviderName.OLLAMA),
        provider=StaticProvider(),
    )
    result = await service.analyze("Можно ли получить консультацию?")
    assert result.provider == "ollama"
    assert result.request_type == RequestType.CONSULTATION

