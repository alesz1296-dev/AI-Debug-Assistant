from functools import lru_cache
from typing import Any, Literal, cast
from uuid import UUID

from redis import Redis
from redis.exceptions import RedisError
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import metrics_registry
from app.core.runtime import AppRuntime, build_runtime
from app.models.records import KnowledgeRecord
from app.schemas.ingestion import (
    DebugCaseIngestionJob,
    DocumentIngestionJob,
    IngestionJobResponse,
    IngestionJobStatus,
    IngestionJobStatusResponse,
    LogIngestionJob,
)
from app.services.retrieval import DatabaseRetriever, InMemoryRetriever

INGESTION_QUEUE_NAME = "ingestion"

_WORKER_RETRIEVER_OVERRIDE: DatabaseRetriever | InMemoryRetriever | None = None


class IngestionQueueUnavailableError(RuntimeError):
    pass


def get_ingestion_queue() -> Queue:
    return Queue(INGESTION_QUEUE_NAME, connection=Redis.from_url(settings.redis_url))


def queue_document_ingestion(payload: DocumentIngestionJob) -> IngestionJobResponse:
    return _queue_job("document", process_document_ingestion, payload, payload.record_id)


def queue_log_ingestion(payload: LogIngestionJob) -> IngestionJobResponse:
    return _queue_job("log", process_log_ingestion, payload, payload.record_id)


def queue_debug_case_ingestion(payload: DebugCaseIngestionJob) -> IngestionJobResponse:
    return _queue_job("debug_case", process_debug_case_ingestion, payload, payload.record_id)


def get_ingestion_job_status(job_id: str) -> IngestionJobStatusResponse:
    try:
        queue = get_ingestion_queue()
        connection = getattr(queue, "connection", None) or Redis.from_url(settings.redis_url)
        job = Job.fetch(job_id, connection=connection)
    except RedisError as exc:
        metrics_registry.record_ingestion_queue_unavailable(
            operation="job_status", kind="unknown"
        )
        get_logger(__name__, component="ingestion_jobs").warning(
            "ingestion.queue_unavailable", operation="job_status", job_id=job_id
        )
        raise IngestionQueueUnavailableError(
            "The ingestion queue is currently unavailable."
        ) from exc
    except NoSuchJobError:
        return IngestionJobStatusResponse(job_id=job_id, status="not_found")

    raw_status = job.get_status(refresh=True)
    status = cast(
        IngestionJobStatus,
        raw_status if raw_status in {"queued", "started", "finished", "failed"} else "queued",
    )
    error_type, error_message = _parse_failure(job.exc_info)
    return IngestionJobStatusResponse(
        job_id=job.id,
        kind=_job_kind_from_payload(job.meta.get("kind")),
        status=status,
        result=str(job.result) if job.result is not None else None,
        error_type=error_type,
        error_message=error_message,
    )


def process_document_ingestion(job_data: dict[str, Any]) -> str:
    payload = DocumentIngestionJob.model_validate(job_data)
    record = KnowledgeRecord(
        id=payload.record_id,
        collection=payload.collection,
        title=payload.title,
        source=payload.source,
        text=payload.text,
        tags=tuple(payload.tags),
        metadata={"synthetic": payload.synthetic},
    )
    saved = _get_worker_retriever().add(record)
    return str(saved.id)


def process_log_ingestion(job_data: dict[str, Any]) -> str:
    payload = LogIngestionJob.model_validate(job_data)
    record = KnowledgeRecord(
        id=payload.record_id,
        collection="system_logs",
        title=f"{payload.service} {payload.severity} log",
        source=f"log://{payload.source_dataset}/{payload.service}",
        text=payload.raw_message,
        tags=tuple(["log", payload.service.lower(), payload.severity.lower(), *payload.tags]),
        metadata={
            "timestamp": payload.timestamp,
            "anomaly_label": payload.anomaly_label,
            "source_dataset": payload.source_dataset,
        },
    )
    saved = _get_worker_retriever().add(record)
    return str(saved.id)


def process_debug_case_ingestion(job_data: dict[str, Any]) -> str:
    payload = DebugCaseIngestionJob.model_validate(job_data)
    tags = [*payload.tags]
    if payload.synthetic and "synthetic" not in tags:
        tags.insert(0, "synthetic")
    record = KnowledgeRecord(
        id=payload.record_id,
        collection="incident_cases",
        title=payload.title,
        source=f"synthetic://debug-case/{payload.record_id}",
        text=" ".join([payload.title, *payload.symptoms, *payload.logs]),
        tags=tuple(tags),
        metadata={
            "kind": "debug_case",
            "synthetic": payload.synthetic,
            "symptoms": payload.symptoms,
            "environment": payload.environment,
            "logs": payload.logs,
            "tags": payload.tags,
        },
    )
    saved = _get_worker_retriever().add(record)
    return str(saved.id)


def set_worker_retriever(retriever: DatabaseRetriever | InMemoryRetriever | None) -> None:
    global _WORKER_RETRIEVER_OVERRIDE
    _WORKER_RETRIEVER_OVERRIDE = retriever


def _queue_job(
    kind: Literal["document", "log", "debug_case"],
    processor: Any,
    payload: DocumentIngestionJob | LogIngestionJob | DebugCaseIngestionJob,
    record_id: UUID,
) -> IngestionJobResponse:
    try:
        queue = get_ingestion_queue()
        job = queue.enqueue(
            processor,
            payload.model_dump(mode="json"),
            job_id=str(record_id),
        )
    except RedisError as exc:
        metrics_registry.record_ingestion_queue_unavailable(operation="enqueue", kind=kind)
        get_logger(__name__, component="ingestion_jobs").warning(
            "ingestion.queue_unavailable",
            operation="enqueue",
            kind=kind,
            record_id=str(record_id),
        )
        raise IngestionQueueUnavailableError(
            "The ingestion queue is currently unavailable."
        ) from exc
    job.meta["kind"] = kind
    cast(Any, job).save_meta()
    return IngestionJobResponse(id=record_id, job_id=job.id, kind=kind, status="queued")


def _get_worker_retriever() -> DatabaseRetriever | InMemoryRetriever:
    if _WORKER_RETRIEVER_OVERRIDE is not None:
        return _WORKER_RETRIEVER_OVERRIDE
    return get_worker_runtime().retriever


def _job_kind_from_payload(kind: Any) -> Literal["document", "log", "debug_case"] | None:
    if kind in {"document", "log", "debug_case"}:
        return cast(Literal["document", "log", "debug_case"], kind)
    return None


def _parse_failure(exc_info: str | None) -> tuple[str | None, str | None]:
    if not exc_info:
        return None, None
    lines = [line for line in exc_info.splitlines() if line.strip()]
    if not lines:
        return None, None
    headline = lines[-1]
    if ": " in headline:
        error_type, error_message = headline.split(": ", 1)
        return error_type.strip(), error_message.strip()
    return None, headline.strip()


@lru_cache(maxsize=1)
def get_worker_runtime() -> AppRuntime:
    return build_runtime(seed=False)
