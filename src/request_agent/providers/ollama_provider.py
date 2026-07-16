from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from pydantic import ValidationError

from request_agent.prompts import SYSTEM_PROMPT, build_user_prompt
from request_agent.providers.base import ProviderError
from request_agent.schemas import LLMResult

# Провайдер инкапсулирует HTTP-вызов Ollama и преобразование недоверенного ответа.

logger = logging.getLogger(__name__)


class OllamaProvider:
    """Получает NLP-результат от локальной Ollama и проверяет её ответ."""

    def __init__(self, base_url: str, model: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout_seconds

    async def analyze(self, text: str) -> LLMResult:
        """Отправляет запрос модели и преобразует ответ в строгую схему."""

        payload = {
            "model": self._model,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(text)},
            ],
            "format": "json",
            "options": {"temperature": 0},
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(f"{self._base_url}/api/chat", json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Ollama request failed: {exc}") from exc

        # Ответ LLM считается недоверенным вводом: модель может нарушить JSON-контракт,
        # вернуть неизвестные enum или значения вне допустимых диапазонов.
        content = self._extract_content(response.json())
        try:
            data = self._extract_json(content)
            return LLMResult.model_validate(data)
        except (json.JSONDecodeError, TypeError, ValidationError) as exc:
            logger.warning("Ollama returned invalid analysis payload: %s", exc)
            raise ProviderError("Ollama returned invalid analysis payload") from exc

    def _extract_content(self, data: dict[str, Any]) -> str:
        """Извлекает строковое содержимое из транспортного ответа Ollama."""

        message = data.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise ProviderError("Ollama response does not contain message.content")
        return message["content"]

    def _extract_json(self, content: str) -> dict[str, Any]:
        """Извлекает JSON-объект, включая ответ с Markdown или вводным текстом."""

        stripped = content.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            return json.loads(stripped)
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise json.JSONDecodeError("JSON object not found", content, 0)
        return json.loads(stripped[start : end + 1])
