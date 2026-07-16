from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from request_agent.utils.text import normalize_text

# Схемы образуют границу доверия для пользовательского ввода и результата провайдера.


class RequestType(StrEnum):
    """Задаёт закрытый набор категорий пользовательских обращений."""

    TECHNICAL_ISSUE = "technical_issue"
    BILLING = "billing"
    ACCOUNT_ACCESS = "account_access"
    COMPLAINT = "complaint"
    CONSULTATION = "consultation"
    FEATURE_REQUEST = "feature_request"
    OTHER = "other"


class Priority(StrEnum):
    """Задаёт допустимые уровни срочности обработки обращения."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalyzeRequest(BaseModel):
    """Валидирует и нормализует входной текст до передачи сервису."""

    text: str = Field(..., min_length=3, max_length=5000)

    @field_validator("text")
    @classmethod
    def normalize_and_validate_text(cls, value: str) -> str:
        """Схлопывает пробелы и проверяет содержательную длину текста."""

        normalized = normalize_text(value)
        if len(normalized) < 3:
            raise ValueError("text must contain at least 3 non-space characters")
        return normalized


class LLMResult(BaseModel):
    """Описывает проверенный результат провайдера без транспортных полей."""

    model_config = ConfigDict(extra="forbid")

    request_type: RequestType
    summary: str = Field(..., min_length=1, max_length=500)
    priority: Priority
    needs_human: bool
    confidence: float = Field(..., ge=0, le=1)

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str) -> str:
        """Приводит summary провайдера к единому пробельному формату."""

        return normalize_text(value)


class AnalyzeResponse(LLMResult):
    """Дополняет результат фактически использованным провайдером."""

    provider: str = Field(..., pattern="^(ollama|mock|mock_fallback)$")
