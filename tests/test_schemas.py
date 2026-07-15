from __future__ import annotations

import pytest
from pydantic import ValidationError

from request_agent.schemas import AnalyzeRequest, LLMResult


def test_request_text_is_normalized() -> None:
    payload = AnalyzeRequest(text="  Не   могу\nвойти   ")
    assert payload.text == "Не могу войти"


@pytest.mark.parametrize("text", ["", "  ", "ab"])
def test_short_or_empty_text_is_invalid(text: str) -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(text=text)


def test_too_long_text_is_invalid() -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(text="a" * 5001)


@pytest.mark.parametrize(
    "data",
    [
        {
            "request_type": "unknown",
            "summary": "Текст.",
            "priority": "low",
            "needs_human": False,
            "confidence": 0.5,
        },
        {
            "request_type": "other",
            "summary": "Текст.",
            "priority": "unknown",
            "needs_human": False,
            "confidence": 0.5,
        },
        {
            "request_type": "other",
            "summary": "Текст.",
            "priority": "low",
            "needs_human": False,
            "confidence": 2,
        },
    ],
)
def test_llm_result_rejects_invalid_values(data: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        LLMResult.model_validate(data)

