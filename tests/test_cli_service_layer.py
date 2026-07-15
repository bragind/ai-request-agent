from __future__ import annotations

from request_agent.config import Settings
from request_agent.schemas import AnalyzeRequest
from request_agent.service import RequestAnalysisService


async def test_cli_and_api_can_share_service_layer() -> None:
    payload = AnalyzeRequest(text="Подскажите, как изменить тариф?")
    result = await RequestAnalysisService(Settings()).analyze(payload.text)
    assert result.request_type == "consultation"
    assert result.provider == "mock"

