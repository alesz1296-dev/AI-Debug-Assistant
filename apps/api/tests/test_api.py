from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_query_returns_grounded_shape() -> None:
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


def test_protected_endpoint_requires_api_key() -> None:
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


def test_evaluation_runs_with_api_key() -> None:
    response = client.post("/api/v1/evaluations/run", headers={"X-API-Key": "dev-local-key"})
    assert response.status_code == 200
    body = response.json()
    assert body["cases_evaluated"] >= 1
    assert body["groundedness_pass_rate"] > 0

