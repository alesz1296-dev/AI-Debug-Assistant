from collections.abc import Callable, Generator
from typing import Any
from uuid import uuid4

import pytest
from app.api import routes as api_routes
from app.core.config import settings
from app.db.base import Base
from app.db.models import KnowledgeRecordRow, RecordEmbeddingRow
from app.main import app
from app.repositories.records import KnowledgeRecordRepository
from app.schemas.ingestion import (
    DebugCaseIngestionJob,
    DocumentIngestionJob,
    IngestionJobResponse,
    LogIngestionJob,
)
from app.services.ingestion_jobs import (
    IngestionQueueUnavailableError,
    get_ingestion_job_status,
    process_debug_case_ingestion,
    process_document_ingestion,
    process_log_ingestion,
    queue_debug_case_ingestion,
    queue_document_ingestion,
    queue_log_ingestion,
    set_worker_retriever,
)
from app.services.retrieval import DatabaseRetriever
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(autouse=True)
def enable_sqlite_fallback() -> Generator[None, None, None]:
    original = settings.allow_sqlite_fallback
    settings.allow_sqlite_fallback = True
    yield
    settings.allow_sqlite_fallback = original


@pytest.fixture(autouse=True)
def clear_worker_retriever() -> Generator[None, None, None]:
    set_worker_retriever(None)
    yield
    set_worker_retriever(None)


@pytest.fixture()
def sqlite_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


class FakeJob:
    def __init__(self, job_id: str) -> None:
        self.id = job_id
        self.meta: dict[str, object] = {}
        self.result: str | None = None

    def save_meta(self) -> None:
        return None


class FakeQueue:
    def __init__(self) -> None:
        self.calls: list[tuple[Callable[[dict[str, Any]], str], dict[str, Any], str]] = []
        self.connection = object()

    def enqueue(
        self,
        func: Callable[[dict[str, Any]], str],
        payload: dict[str, Any],
        job_id: str,
    ) -> FakeJob:
        self.calls.append((func, payload, job_id))
        return FakeJob(job_id)


def test_queue_document_ingestion_uses_job_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    queue = FakeQueue()
    monkeypatch.setattr("app.services.ingestion_jobs.get_ingestion_queue", lambda: queue)
    payload = DocumentIngestionJob(
        record_id=uuid4(),
        collection="knowledge_base",
        title="Queue test",
        source="docs/queue-test.md",
        text="This is enough content to satisfy validation and queueing.",
        tags=["queue"],
        synthetic=False,
    )

    response = queue_document_ingestion(payload)

    assert response == IngestionJobResponse(
        id=payload.record_id,
        job_id=str(payload.record_id),
        kind="document",
        status="queued",
    )
    assert queue.calls[0][0] is process_document_ingestion
    assert queue.calls[0][1]["record_id"] == str(payload.record_id)
    assert queue.calls[0][2] == str(payload.record_id)


def test_queue_log_ingestion_uses_job_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    queue = FakeQueue()
    monkeypatch.setattr("app.services.ingestion_jobs.get_ingestion_queue", lambda: queue)
    payload = LogIngestionJob(
        record_id=uuid4(),
        service="worker",
        raw_message="queue depth above threshold",
        severity="WARN",
    )

    response = queue_log_ingestion(payload)

    assert response.kind == "log"
    assert response.status == "queued"
    assert queue.calls[0][0] is process_log_ingestion


def test_queue_debug_case_ingestion_uses_job_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    queue = FakeQueue()
    monkeypatch.setattr("app.services.ingestion_jobs.get_ingestion_queue", lambda: queue)
    payload = DebugCaseIngestionJob(
        record_id=uuid4(),
        title="Queue case",
        symptoms=["timeouts"],
        logs=["worker retry storm"],
    )

    response = queue_debug_case_ingestion(payload)

    assert response.kind == "debug_case"
    assert response.status == "queued"
    assert queue.calls[0][0] is process_debug_case_ingestion


def test_process_document_ingestion_persists_record_and_embedding(
    sqlite_session: Session,
) -> None:
    set_worker_retriever(DatabaseRetriever(sqlite_session))
    payload = DocumentIngestionJob(
        record_id=uuid4(),
        collection="knowledge_base",
        title="Worker document",
        source="docs/worker-document.md",
        text="This document explains the worker path for ingestion and persistence.",
        tags=["worker", "docs"],
        synthetic=False,
    )

    result = process_document_ingestion(payload.model_dump(mode="json"))

    assert result == str(payload.record_id)
    record = sqlite_session.get(KnowledgeRecordRow, str(payload.record_id))
    assert record is not None
    embedding_id = sqlite_session.scalar(
        select(RecordEmbeddingRow.id).where(RecordEmbeddingRow.record_id == str(payload.record_id))
    )
    assert embedding_id is not None


def test_process_log_ingestion_persists_record(sqlite_session: Session) -> None:
    set_worker_retriever(DatabaseRetriever(sqlite_session))
    payload = LogIngestionJob(
        record_id=uuid4(),
        service="api",
        raw_message="2026-05-28T10:00:00Z api WARN queue depth above threshold",
        severity="WARN",
        source_dataset="local_demo",
    )

    result = process_log_ingestion(payload.model_dump(mode="json"))

    assert result == str(payload.record_id)
    repository = KnowledgeRecordRepository(sqlite_session)
    record = repository.get(payload.record_id)
    assert record is not None
    assert record.source == "log://local_demo/api"


def test_process_debug_case_ingestion_persists_record(sqlite_session: Session) -> None:
    set_worker_retriever(DatabaseRetriever(sqlite_session))
    payload = DebugCaseIngestionJob(
        record_id=uuid4(),
        title="Debug case",
        symptoms=["timeouts", "queue growth"],
        logs=["worker retry storm"],
        tags=["synthetic"],
    )

    result = process_debug_case_ingestion(payload.model_dump(mode="json"))

    assert result == str(payload.record_id)
    record = KnowledgeRecordRepository(sqlite_session).get(payload.record_id)
    assert record is not None
    assert record.collection == "incident_cases"
    assert "queue growth" in record.text


def test_documents_route_enqueues_work(monkeypatch: pytest.MonkeyPatch) -> None:
    response_payload = IngestionJobResponse(
        id=uuid4(),
        job_id="job-123",
        kind="document",
        status="queued",
    )
    monkeypatch.setattr(api_routes, "queue_document_ingestion", lambda payload: response_payload)

    client = TestClient(app)
    response = client.post(
        "/api/v1/documents",
        headers={"X-API-Key": "dev-local-key"},
        json={
            "collection": "knowledge_base",
            "title": "Queue via route",
            "source": "docs/route-queue.md",
            "text": "This text is long enough to pass validation.",
            "tags": ["route"],
            "synthetic": False,
        },
    )

    assert response.status_code == 200
    assert response.json() == response_payload.model_dump(mode="json")


def test_ingestion_job_status_reports_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeStatusJob:
        id = "job-123"
        result = None
        exc_info = "Traceback...\nValueError: bad payload"
        meta = {"kind": "document"}

        def get_status(self, refresh: bool = True) -> str:
            return "failed"

    queue = FakeQueue()
    monkeypatch.setattr("app.services.ingestion_jobs.get_ingestion_queue", lambda: queue)
    
    def fake_fetch(job_id: str, connection: object) -> FakeStatusJob:
        return FakeStatusJob()

    monkeypatch.setattr("app.services.ingestion_jobs.Job.fetch", fake_fetch)

    response = get_ingestion_job_status("job-123")

    assert response.status == "failed"
    assert response.kind == "document"
    assert response.error_type == "ValueError"
    assert response.error_message == "bad payload"


def test_queue_document_ingestion_raises_when_redis_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BrokenQueue:
        def enqueue(self, func: object, payload: dict[str, Any], job_id: str) -> object:
            raise RedisConnectionError("redis down")

    monkeypatch.setattr("app.services.ingestion_jobs.get_ingestion_queue", lambda: BrokenQueue())
    payload = DocumentIngestionJob(
        record_id=uuid4(),
        collection="knowledge_base",
        title="Queue unavailable",
        source="docs/queue-unavailable.md",
        text="This is enough content to satisfy validation while Redis is down.",
    )

    with pytest.raises(IngestionQueueUnavailableError):
        queue_document_ingestion(payload)


def test_documents_route_returns_503_when_queue_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        api_routes,
        "queue_document_ingestion",
        lambda payload: (_ for _ in ()).throw(
            IngestionQueueUnavailableError("The ingestion queue is currently unavailable.")
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/documents",
        headers={"X-API-Key": "dev-local-key"},
        json={
            "collection": "knowledge_base",
            "title": "Queue via route",
            "source": "docs/route-queue.md",
            "text": "This text is long enough to pass validation.",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"]["error"] == "queue_unavailable"


def test_ingestion_job_status_route_returns_503_when_queue_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        api_routes,
        "get_ingestion_job_status",
        lambda job_id: (_ for _ in ()).throw(
            IngestionQueueUnavailableError("The ingestion queue is currently unavailable.")
        ),
    )

    client = TestClient(app)
    response = client.get(
        "/api/v1/ingestion-jobs/job-123",
        headers={"X-API-Key": "dev-local-key"},
    )

    assert response.status_code == 503
    assert response.json()["detail"]["error"] == "queue_unavailable"
