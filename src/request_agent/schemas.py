from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from request_agent.utils.text import normalize_text


class RequestType(StrEnum):
    TECHNICAL_ISSUE = "technical_issue"
    BILLING = "billing"
    ACCOUNT_ACCESS = "account_access"
    COMPLAINT = "complaint"
    CONSULTATION = "consultation"
    FEATURE_REQUEST = "feature_request"
    OTHER = "other"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=5000)

    @field_validator("text")
    @classmethod
    def normalize_and_validate_text(cls, value: str) -> str:
        normalized = normalize_text(value)
        if len(normalized) < 3:
            raise ValueError("text must contain at least 3 non-space characters")
        return normalized


class LLMResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_type: RequestType
    summary: str = Field(..., min_length=1, max_length=500)
    priority: Priority
    needs_human: bool
    confidence: float = Field(..., ge=0, le=1)

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str) -> str:
        return normalize_text(value)


class AnalyzeResponse(LLMResult):
    provider: str = Field(..., pattern="^(ollama|mock|mock_fallback)$")

