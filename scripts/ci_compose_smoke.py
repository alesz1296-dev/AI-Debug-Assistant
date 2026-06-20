from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "infra" / "docker-compose.yml"
COMPOSE_PROJECT = os.environ.get("COMPOSE_SMOKE_PROJECT", "ai-debug-assistant-smoke")
BASE_URL = "http://127.0.0.1:8000/api/v1"
API_KEY = "dev-local-key"


def main() -> int:
    worker_output = ""
    try:
        compose("down", "--volumes", "--remove-orphans", check=False)
        compose("build", "api")
        compose("up", "-d", "postgres", "redis")
        wait_for_postgres()
        compose("run", "--rm", "-T", "api", "alembic", "-c", "alembic.ini", "upgrade", "head")
        compose("up", "-d", "api")
        wait_for_health()
        assert_health()
        assert_ready()
        assert_metrics_surface()

        job_id = enqueue_document()
        worker_output = run_worker_burst()
        wait_for_job_finished(job_id)
        assert_query()
        assert_evaluation()
        assert_metrics_counters()
        assert_api_logs()
        assert_worker_logs(worker_output)
    finally:
        compose("down", "--volumes", "--remove-orphans", check=False)
        if worker_output:
            print("---- worker output ----")
            print(worker_output)
    return 0


def compose(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = ["docker", "compose", "-p", COMPOSE_PROJECT, "-f", str(COMPOSE_FILE), *args]
    print("+", " ".join(command), flush=True)
    return subprocess.run(
        command,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=None,
        stderr=None,
    )


def wait_for_health() -> None:
    deadline = time.monotonic() + 90
    last_error = ""
    while time.monotonic() < deadline:
        try:
            response = request_json("GET", "/health")
            if response.get("status") == "ok":
                return
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
        time.sleep(2)
    raise AssertionError(f"API did not become healthy in time. Last error: {last_error}")


def wait_for_postgres() -> None:
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        result = compose(
            "exec",
            "-T",
            "postgres",
            "pg_isready",
            "-U",
            "debug",
            "-d",
            "debug_assistant",
            check=False,
        )
        if result.returncode == 0:
            return
        time.sleep(2)
    raise AssertionError("Postgres did not become ready in time.")


def assert_health() -> None:
    response = request_json("GET", "/health")
    assert_equal(response.get("status"), "ok", "health status")
    assert_equal(response.get("backend"), "postgresql", "health backend")


def assert_ready() -> None:
    response = request_json("GET", "/ready")
    assert_equal(response.get("status"), "ok", "ready status")
    assert_equal(response.get("backend"), "postgresql", "ready backend")
    dependencies = response.get("dependencies", {})
    assert_equal(dependencies.get("database"), "ok", "ready database")
    assert_equal(dependencies.get("redis_queue"), "ok", "ready redis queue")


def assert_metrics_surface() -> None:
    metrics = request_text("GET", "/metrics")
    assert_contains(metrics, "enterprise_ai_http_requests_total", "metrics HTTP counter")


def run_worker_burst() -> str:
    command = [
        "docker",
        "compose",
        "-p",
        COMPOSE_PROJECT,
        "-f",
        str(COMPOSE_FILE),
        "run",
        "--rm",
        "-T",
        "-e",
        "PYTHONUNBUFFERED=1",
        "api",
        "python",
        "-m",
        "app.workers.ingestion",
        "--burst",
    ]
    print("+", " ".join(command), flush=True)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout


def enqueue_document() -> str:
    response = request_json(
        "POST",
        "/documents",
        body={
            "collection": "knowledge_base",
            "title": "CI compose smoke runbook",
            "source": "ci://compose-smoke/runbook",
            "text": (
                "When workers are delayed, inspect queue depth, retry rate, "
                "worker concurrency, and downstream dependency latency."
            ),
            "tags": ["ci", "smoke", "worker"],
            "synthetic": True,
        },
        headers=auth_headers(),
    )
    assert_equal(response.get("kind"), "document", "ingestion kind")
    assert_equal(response.get("status"), "queued", "ingestion queue status")
    job_id = response.get("job_id")
    if not isinstance(job_id, str) or not job_id:
        raise AssertionError(f"Expected non-empty job_id, got {job_id!r}")
    return job_id


def wait_for_job_finished(job_id: str) -> None:
    deadline = time.monotonic() + 60
    last_response: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        response = request_json("GET", f"/ingestion-jobs/{job_id}", headers=auth_headers())
        last_response = response
        if response.get("status") == "finished":
            return
        if response.get("status") == "failed":
            raise AssertionError(f"Ingestion job failed: {response}")
        time.sleep(2)
    raise AssertionError(f"Ingestion job did not finish in time. Last response: {last_response}")


def assert_query() -> None:
    response = request_json(
        "POST",
        "/query",
        body={
            "question": (
                "The API is timing out and workers are backing up after a deploy. "
                "What should I check?"
            ),
            "top_k": 5,
        },
    )
    if not response.get("citations"):
        raise AssertionError("Expected query response to include citations.")
    assert_contains(json.dumps(response), "CI compose smoke runbook", "query citation")


def assert_evaluation() -> None:
    response = request_json("POST", "/evaluations/run", headers=auth_headers())
    assert_equal(response.get("passed"), True, "evaluation passed")
    assert_equal(response.get("cases_evaluated"), 5, "evaluation case count")
    assert_contains(
        json.dumps(response.get("thresholds", {})),
        "min_no_evidence_case_warning_rate",
        "renamed no-evidence threshold",
    )


def assert_metrics_counters() -> None:
    metrics = request_text("GET", "/metrics")
    required = [
        "enterprise_ai_http_requests_total",
        "enterprise_ai_query_requests_total 1",
        'enterprise_ai_ingestion_enqueue_success_total{kind="document"} 1',
        "enterprise_ai_evaluation_runs_total 1",
        "enterprise_ai_evaluation_runs_passed_total 1",
    ]
    for expected in required:
        assert_contains(metrics, expected, f"metrics line {expected}")


def assert_api_logs() -> None:
    logs = subprocess.run(
        ["docker", "compose", "-p", COMPOSE_PROJECT, "-f", str(COMPOSE_FILE), "logs", "api"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout
    for expected in [
        "request_id",
        "readiness.checked",
        "query.completed",
        "evaluation.completed",
        "ingestion.queued",
    ]:
        assert_contains(logs, expected, f"API log event {expected}")


def assert_worker_logs(output: str) -> None:
    assert_contains(output, "worker.started", "worker startup log")
    assert_contains(output, "ingestion.job.succeeded", "worker success log")


def request_json(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    response = request(method, path, body=body, headers=headers)
    return cast(dict[str, Any], json.loads(response))


def request_text(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> str:
    return request(method, path, body=body, headers=headers)


def request(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> str:
    data = None
    merged_headers = {"Accept": "application/json"}
    if headers:
        merged_headers.update(headers)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        merged_headers["Content-Type"] = "application/json"
    request_obj = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=merged_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request_obj, timeout=10) as response:
            text = cast(str, response.read().decode("utf-8"))
            return text
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        raise AssertionError(f"{method} {path} returned {exc.code}: {text}") from exc


def auth_headers() -> dict[str, str]:
    return {"X-API-Key": API_KEY}


def assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"Expected {label} to be {expected!r}, got {actual!r}")


def assert_contains(value: str, expected: str, label: str) -> None:
    if expected not in value:
        raise AssertionError(f"Expected {label} to contain {expected!r}.")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"compose smoke failed: {exc}", file=sys.stderr)
        raise
