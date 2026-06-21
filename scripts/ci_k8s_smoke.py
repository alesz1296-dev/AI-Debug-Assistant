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
CHART_DIR = ROOT / "infra" / "helm" / "ai-debug-assistant"
VALUES_FILE = CHART_DIR / "values-kind.yaml"
IMAGE_REF = "ai-debug-assistant-api:local"
BASE_URL = "http://127.0.0.1:8000/api/v1"
API_KEY = "dev-local-key"
CLUSTER_NAME = os.environ.get("K8S_SMOKE_CLUSTER", "ai-debug-ci")
RELEASE_NAME = os.environ.get("K8S_SMOKE_RELEASE", "ai-debug-assistant")
NAMESPACE = os.environ.get("K8S_SMOKE_NAMESPACE", "ai-debug")
FULLNAME = os.environ.get("K8S_SMOKE_FULLNAME", "ai-debug")
RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 15


def main() -> int:
    port_forward: subprocess.Popen[str] | None = None
    try:
        kind("delete", "cluster", "--name", CLUSTER_NAME, check=False)
        retry_command("kind create cluster", kind, "create", "cluster", "--name", CLUSTER_NAME)
        retry_command(
            "docker build api image",
            run,
            "docker",
            "build",
            "-f",
            "infra/Dockerfile.api",
            "-t",
            IMAGE_REF,
            ".",
            cwd=ROOT,
        )
        retry_command(
            "kind load docker image",
            kind,
            "load",
            "docker-image",
            IMAGE_REF,
            "--name",
            CLUSTER_NAME,
        )
        helm(
            "template",
            RELEASE_NAME,
            str(CHART_DIR),
            "--namespace",
            NAMESPACE,
            "-f",
            str(VALUES_FILE),
        )
        helm(
            "upgrade",
            "--install",
            RELEASE_NAME,
            str(CHART_DIR),
            "--namespace",
            NAMESPACE,
            "--create-namespace",
            "-f",
            str(VALUES_FILE),
            "--wait",
            "--wait-for-jobs",
            "--timeout",
            "240s",
        )
        wait_for_rollout("deployment", f"{FULLNAME}-postgres")
        wait_for_rollout("deployment", f"{FULLNAME}-redis")
        wait_for_rollout("deployment", f"{FULLNAME}-api")
        wait_for_rollout("deployment", f"{FULLNAME}-worker")
        wait_for_migration_job()

        port_forward = start_port_forward()
        wait_for_health()
        assert_health()
        assert_ready()
        assert_metrics_surface()
        assert_query()
        assert_evaluation()
        assert_unauthorized()
        job_id = enqueue_document()
        wait_for_job_finished(job_id)
        assert_metrics_counters()
        assert_api_logs()
        assert_worker_logs()
    except Exception:
        dump_diagnostics()
        raise
    finally:
        stop_port_forward(port_forward)
        kind("delete", "cluster", "--name", CLUSTER_NAME, check=False)
    return 0


def run(*args: str, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(args), flush=True)
    return subprocess.run(
        list(args),
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def retry_command(
    label: str,
    runner: Any,
    *args: str,
    **kwargs: Any,
) -> subprocess.CompletedProcess[str]:
    last_error: subprocess.CalledProcessError | None = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            return cast(subprocess.CompletedProcess[str], runner(*args, **kwargs))
        except subprocess.CalledProcessError as exc:
            last_error = exc
            if attempt == RETRY_ATTEMPTS:
                break
            print(
                f"{label} failed on attempt {attempt}/{RETRY_ATTEMPTS}; "
                f"retrying in {RETRY_DELAY_SECONDS}s",
                flush=True,
            )
            time.sleep(RETRY_DELAY_SECONDS)
    assert last_error is not None
    raise last_error


def kind(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run("kind", *args, check=check)


def kubectl(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run("kubectl", *args, check=check)


def helm(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run("helm", *args, check=check)


def wait_for_rollout(resource_kind: str, name: str) -> None:
    kubectl(
        "rollout",
        "status",
        f"{resource_kind}/{name}",
        "-n",
        NAMESPACE,
        "--timeout=180s",
    )


def wait_for_migration_job() -> None:
    job_name = migration_job_name()
    kubectl(
        "wait",
        "--for=condition=complete",
        f"job/{job_name}",
        "-n",
        NAMESPACE,
        "--timeout=180s",
    )


def migration_job_name() -> str:
    output = kubectl(
        "get",
        "jobs",
        "-n",
        NAMESPACE,
        "-l",
        "app.kubernetes.io/component=migration",
        "-o",
        "json",
    ).stdout
    payload = json.loads(output)
    items = payload.get("items", [])
    if len(items) != 1:
        raise AssertionError(f"Expected one migration job, found {len(items)}.")
    return items[0]["metadata"]["name"]


def start_port_forward() -> subprocess.Popen[str]:
    command = [
        "kubectl",
        "port-forward",
        f"service/{FULLNAME}-api",
        "8000:8000",
        "-n",
        NAMESPACE,
    ]
    print("+", " ".join(command), flush=True)
    return subprocess.Popen(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop_port_forward(process: subprocess.Popen[str] | None) -> None:
    if process is None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


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
    raise AssertionError(f"Kubernetes API did not become healthy in time. Last error: {last_error}")


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


def assert_evaluation() -> None:
    response = request_json("POST", "/evaluations/run", headers=auth_headers())
    assert_equal(response.get("passed"), True, "evaluation passed")
    assert_equal(response.get("cases_evaluated"), 5, "evaluation case count")
    assert_contains(
        json.dumps(response.get("thresholds", {})),
        "min_no_evidence_case_warning_rate",
        "renamed no-evidence threshold",
    )


def assert_unauthorized() -> None:
    status_code, body = request_allow_error("POST", "/evaluations/run")
    assert_equal(status_code, 401, "unauthorized status")
    assert_contains(body, "Missing or invalid API key", "unauthorized response body")


def enqueue_document() -> str:
    response = request_json(
        "POST",
        "/documents",
        body={
            "collection": "knowledge_base",
            "title": "CI kubernetes smoke runbook",
            "source": "ci://k8s-smoke/runbook",
            "text": (
                "When workers are delayed, inspect queue depth, retry rate, "
                "worker concurrency, and downstream dependency latency."
            ),
            "tags": ["ci", "smoke", "worker", "kubernetes"],
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
    deadline = time.monotonic() + 90
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
    logs = kubectl("logs", f"deployment/{FULLNAME}-api", "-n", NAMESPACE).stdout
    for expected in [
        "request_id",
        "readiness.checked",
        "query.completed",
        "evaluation.completed",
        "ingestion.queued",
    ]:
        assert_contains(logs, expected, f"API log event {expected}")


def assert_worker_logs() -> None:
    logs = kubectl("logs", f"deployment/{FULLNAME}-worker", "-n", NAMESPACE).stdout
    for expected in ["worker.started", "ingestion.job.succeeded"]:
        assert_contains(logs, expected, f"worker log event {expected}")


def dump_diagnostics() -> None:
    print("---- kubernetes diagnostics ----", file=sys.stderr)
    for command in [
        ["kubectl", "get", "all,pvc", "-n", NAMESPACE],
        ["kubectl", "get", "pods", "-n", NAMESPACE, "-o", "wide"],
        ["kubectl", "logs", f"deployment/{FULLNAME}-api", "-n", NAMESPACE],
        ["kubectl", "logs", f"deployment/{FULLNAME}-worker", "-n", NAMESPACE],
    ]:
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            print(f"+ {' '.join(command)}", file=sys.stderr)
            print(completed.stdout, file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            print(f"failed to collect diagnostics for {' '.join(command)}: {exc}", file=sys.stderr)


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


def request_allow_error(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, str]:
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
            return response.status, cast(str, response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def request(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> str:
    status_code, response = request_allow_error(method, path, body=body, headers=headers)
    if status_code >= 400:
        raise AssertionError(f"{method} {path} returned {status_code}: {response}")
    return response


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
        print(f"kubernetes smoke failed: {exc}", file=sys.stderr)
        raise
