from __future__ import annotations

from fastapi.testclient import TestClient

from request_agent.api import app


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "llm_provider": "mock"}


def test_analyze_returns_expected_schema() -> None:
    response = TestClient(app).post(
        "/api/v1/requests/analyze",
        json={"text": "Не могу войти в личный кабинет, появляется ошибка 403. Срочно помогите."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["request_type"] == "account_access"
    assert data["priority"] == "high"
    assert data["needs_human"] is True
    assert data["provider"] == "mock"
    assert set(data) == {
        "request_type",
        "summary",
        "priority",
        "needs_human",
        "confidence",
        "provider",
    }


def test_invalid_input_returns_422() -> None:
    response = TestClient(app).post("/api/v1/requests/analyze", json={"text": "  "})
    assert response.status_code == 422
