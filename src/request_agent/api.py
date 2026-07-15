from __future__ import annotations

import logging

from fastapi import APIRouter, FastAPI

from request_agent.config import get_settings
from request_agent.schemas import AnalyzeRequest, AnalyzeResponse
from request_agent.service import RequestAnalysisService

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

settings = get_settings()
app = FastAPI(title="AI Request Agent", version="0.1.0")
router = APIRouter(prefix="/api/v1/requests", tags=["requests"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "llm_provider": settings.llm_provider.value}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_request(payload: AnalyzeRequest) -> AnalyzeResponse:
    service = RequestAnalysisService(settings)
    return await service.analyze(payload.text)


app.include_router(router)

