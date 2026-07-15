from __future__ import annotations

import asyncio
import json
import logging

from pydantic import ValidationError

from request_agent.config import get_settings
from request_agent.schemas import AnalyzeRequest
from request_agent.service import RequestAnalysisService

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


async def run_cli() -> int:
    text = input("Введите текст обращения: ")
    try:
        payload = AnalyzeRequest(text=text)
    except ValidationError as exc:
        error_payload = {"error": "validation_error", "details": exc.errors()}
        print(json.dumps(error_payload, ensure_ascii=False))
        return 1

    service = RequestAnalysisService(get_settings())
    result = await service.analyze(payload.text)
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(run_cli()))


if __name__ == "__main__":
    main()
