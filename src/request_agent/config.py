from __future__ import annotations

from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Модуль изолирует чтение окружения от выбора и работы конкретного провайдера.


class LLMProviderName(StrEnum):
    """Перечисляет поддерживаемые источники анализа обращений."""

    MOCK = "mock"
    OLLAMA = "ollama"


class Settings(BaseSettings):
    """Хранит настройки выбора провайдера и подключения к локальной Ollama."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: LLMProviderName = LLMProviderName.MOCK
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_timeout_seconds: float = Field(default=15.0, gt=0)


def get_settings() -> Settings:
    """Создаёт настройки из переменных окружения и значений по умолчанию."""

    return Settings()
