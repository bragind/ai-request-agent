from __future__ import annotations

from typing import Protocol

from request_agent.schemas import LLMResult


class ProviderError(RuntimeError):
    pass


class LLMProvider(Protocol):
    async def analyze(self, text: str) -> LLMResult:
        raise NotImplementedError

