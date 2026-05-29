import json

import pytest
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.main import app
from fastapi.testclient import TestClient


def test_structured_logging_outputs_json(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO")

    get_logger("test", component="unit").info("unit.event", answer=42)

    output = capsys.readouterr().out.strip().splitlines()[-1]
    payload = json.loads(output)
    assert payload["event"] == "unit.event"
    assert payload["component"] == "unit"
    assert payload["answer"] == 42
    assert payload["level"] == "info"
    assert "timestamp" in payload


def test_request_log_includes_request_id(capsys: pytest.CaptureFixture[str]) -> None:
    settings.allow_sqlite_fallback = True
    with TestClient(app) as client:
        response = client.get("/api/v1/health", headers={"X-Request-ID": "req-log-123"})

    assert response.status_code == 200
    lines = [json.loads(line) for line in capsys.readouterr().out.strip().splitlines() if line]
    request_logs = [line for line in lines if line.get("event") == "http.request.completed"]
    assert request_logs
    payload = request_logs[-1]
    assert payload["request_id"] == "req-log-123"
    assert payload["method"] == "GET"
    assert payload["path"] == "/api/v1/health"
    assert payload["status_code"] == 200
    assert "latency_ms" in payload
