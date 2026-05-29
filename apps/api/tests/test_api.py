from collections.abc import Generator
from typing import Any

import pytest
from app.api import routes as api_routes
from app.core.config import settings
from app.core.metrics import metrics_registry
from app.main import app
from app.schemas.ingestion import IngestionJobResponse
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def enable_sqlite_fallback() -> Generator[None, None, None]:
    original = settings.allow_sqlite_fallback
    settings.allow_sqlite_fallback = True
    metrics_registry.reset()
    yield
    settings.allow_sqlite_fallback = original
    metrics_registry.reset()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["backend"] in {"sqlite_fallback", "sqlite", "postgresql"}
    assert response.headers["X-Request-ID"]


def test_ready_returns_ok_when_dependencies_are_available(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(api_routes, "_runtime_ready", lambda request: True)
    monkeypatch.setattr(api_routes, "_database_ready", lambda request: True)
    monkeypatch.setattr(api_routes, "_queue_ready", lambda: True)

    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["dependencies"]["runtime"] == "ok"
    assert body["dependencies"]["database"] == "ok"
    assert body["dependencies"]["redis_queue"] == "ok"


def test_ready_returns_503_when_dependency_is_degraded(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(api_routes, "_runtime_ready", lambda request: True)
    monkeypatch.setattr(api_routes, "_database_ready", lambda request: True)
    monkeypatch.setattr(api_routes, "_queue_ready", lambda: False)

    response = client.get("/api/v1/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["dependencies"]["redis_queue"] == "unavailable"


def test_query_returns_grounded_shape(client: TestClient) -> None:
    response = client.post(
        "/api/v1/query",
        json={"question": "The API is timing out and the Redis queue is growing after a deploy."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert body["citations"]
    assert "retrieval_trace_id" in body
    assert "next_steps" in body
    assert any(
        citation["title"] == "Synthetic queue backlog after deploy"
        for citation in body["citations"]
    )


def test_protected_endpoint_requires_api_key(client: TestClient) -> None:
    response = client.post(
        "/api/v1/documents",
        json={
            "collection": "knowledge_base",
            "title": "Runbook test",
            "source": "docs/test.md",
            "text": "This is enough content to satisfy validation.",
        },
    )
    assert response.status_code == 401


def test_evaluation_runs_with_api_key(client: TestClient) -> None:
    response = client.post("/api/v1/evaluations/run", headers={"X-API-Key": "dev-local-key"})
    assert response.status_code == 200
    body = response.json()
    assert body["cases_evaluated"] >= 1
    assert body["groundedness_pass_rate"] > 0
    assert body["citation_presence_rate"] > 0
    assert body["mean_latency_ms"] >= 0
    assert body["weak_evidence_warning_rate"] >= 0
    assert body["no_evidence_warning_rate"] >= 0
    assert "passed" in body
    assert body["thresholds"]["min_mean_retrieval_score"] == 0.67
    assert "min_no_evidence_warning_rate" in body["thresholds"]


def test_debug_case_round_trips_from_durable_storage(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_queue(payload: Any) -> IngestionJobResponse:
        return IngestionJobResponse(
            id=payload.record_id,
            job_id=str(payload.record_id),
            kind="debug_case",
            status="queued",
        )

    monkeypatch.setattr(api_routes, "queue_debug_case_ingestion", fake_queue)

    created = client.post(
        "/api/v1/debug-cases",
        headers={"X-API-Key": "dev-local-key"},
        json={
            "title": "Worker retries spike after deploy",
            "symptoms": ["timeouts", "queue growth"],
            "environment": {"service": "api"},
            "logs": ["worker retry storm"],
            "tags": ["manual", "queue"],
            "synthetic": True,
        },
    )

    assert created.status_code == 200
    debug_case = created.json()

    loaded = client.get(
        f"/api/v1/debug-cases/{debug_case['id']}",
        headers={"X-API-Key": "dev-local-key"},
    )

    assert loaded.status_code == 200
    assert loaded.json() == debug_case


def test_debug_case_missing_returns_404(client: TestClient) -> None:
    response = client.get(
        "/api/v1/debug-cases/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        headers={"X-API-Key": "dev-local-key"},
    )

    assert response.status_code == 404


def test_request_id_is_propagated_when_provided(client: TestClient) -> None:
    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": "req-from-client-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-from-client-123"


def test_metrics_endpoint_reports_http_and_query_metrics(client: TestClient) -> None:
    client.get("/api/v1/health")
    client.post(
        "/api/v1/query",
        json={"question": "The API is timing out and the Redis queue is growing after a deploy."},
    )

    response = client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert (
        response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
    )
    body = response.text
    assert (
        'enterprise_ai_http_requests_total'
        '{method="GET",path="/api/v1/health",status_code="200"} 1'
    ) in body
    assert "enterprise_ai_query_requests_total 1" in body
    assert "enterprise_ai_query_latency_ms_count 1" in body


def test_metrics_endpoint_reports_evaluation_metrics(client: TestClient) -> None:
    response = client.post("/api/v1/evaluations/run", headers={"X-API-Key": "dev-local-key"})
    assert response.status_code == 200

    metrics = client.get("/api/v1/metrics")
    body = metrics.text

    assert "enterprise_ai_evaluation_runs_total 1" in body
    if response.json()["passed"]:
        assert "enterprise_ai_evaluation_runs_passed_total 1" in body
    else:
        assert "enterprise_ai_evaluation_runs_failed_total 1" in body

