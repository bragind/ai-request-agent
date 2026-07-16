from __future__ import annotations

import logging

from fastapi import APIRouter, FastAPI

from request_agent.config import get_settings
from request_agent.schemas import AnalyzeRequest, AnalyzeResponse
from request_agent.service import RequestAnalysisService

# HTTP-слой отвечает за маршрутизацию и схемы, не дублируя анализ обращений.

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

settings = get_settings()
app = FastAPI(title="AI Request Agent", version="0.1.0")
router = APIRouter(prefix="/api/v1/requests", tags=["requests"])


@app.get("/health")
async def health() -> dict[str, str]:
    """Сообщает состояние приложения и настроенный основной провайдер."""

    return {"status": "ok", "llm_provider": settings.llm_provider.value}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_request(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Передаёт проверенный HTTP-ввод в общий сервис анализа обращений."""

    # API отвечает только за транспорт и делегирует бизнес-логику сервису,
    # который также используется CLI и гарантирует одинаковый JSON-контракт.
    service = RequestAnalysisService(settings)
    return await service.analyze(payload.text)


app.include_router(router)
