from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import metrics_registry
from app.core.security import require_api_key
from app.models.records import KnowledgeRecord
from app.repositories.records import KnowledgeRecordRepository
from app.schemas.debug import (
    DebugCase,
    DebugCaseCreate,
    DocumentIngestRequest,
    EvaluationRunResponse,
    LogIngestRequest,
    QueryRequest,
    QueryResponse,
)
from app.schemas.ingestion import (
    DebugCaseIngestionJob,
    DocumentIngestionJob,
    IngestionJobResponse,
    IngestionJobStatusResponse,
    LogIngestionJob,
)
from app.services.evaluation import run_evaluation
from app.services.ingestion_jobs import (
    IngestionQueueUnavailableError,
    get_ingestion_job_status,
    queue_debug_case_ingestion,
    queue_document_ingestion,
    queue_log_ingestion,
)
from app.services.rag import assistant
from app.services.retrieval import DatabaseRetriever

router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict[str, str]:
    backend_name = getattr(request.app.state.runtime, "backend_name", "unknown")
    return {
        "status": "ok",
        "service": "enterprise-ai-debug-assistant",
        "backend": backend_name,
    }


@router.get("/metrics")
def metrics() -> Response:
    return Response(
        content=metrics_registry.render_prometheus(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@router.get("/ready")
def ready(request: Request) -> JSONResponse:
    runtime_ready = _runtime_ready(request)
    database_ready = _database_ready(request) if runtime_ready else False
    queue_ready = _queue_ready()
    backend_name = getattr(getattr(request.app.state, "runtime", None), "backend_name", "unknown")
    degraded_reasons: list[str] = []
    if not runtime_ready:
        degraded_reasons.append("runtime")
    if runtime_ready and not database_ready:
        degraded_reasons.append("database")
    if not queue_ready:
        degraded_reasons.append("redis_queue")
    status_code = (
        status.HTTP_200_OK
        if runtime_ready and database_ready and queue_ready
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    payload: dict[str, Any] = {
        "status": "ok" if status_code == status.HTTP_200_OK else "degraded",
        "service": "enterprise-ai-debug-assistant",
        "backend": backend_name,
        "dependencies": {
            "runtime": "ok" if runtime_ready else "unavailable",
            "database": "ok" if database_ready else "unavailable",
            "redis_queue": "ok" if queue_ready else "unavailable",
        },
    }
    metrics_registry.record_readiness_check(payload["status"], degraded_reasons)
    get_logger(__name__, component="api.routes").info(
        "readiness.checked",
        status=payload["status"],
        backend=backend_name,
        runtime_ready=runtime_ready,
        database_ready=database_ready,
        queue_ready=queue_ready,
        degraded_reasons=degraded_reasons,
    )
    return JSONResponse(status_code=status_code, content=payload)


@router.post("/debug-cases", response_model=DebugCase, dependencies=[Depends(require_api_key)])
def create_debug_case(request: Request, payload: DebugCaseCreate) -> DebugCase:
    debug_case = DebugCase(id=uuid4(), **payload.model_dump())
    with request.app.state.runtime.session_factory() as session:
        repository = KnowledgeRecordRepository(session)
        repository.upsert_by_source(_debug_case_record(debug_case))
        session.commit()
    try:
        job = queue_debug_case_ingestion(
            DebugCaseIngestionJob(
                record_id=debug_case.id,
                title=debug_case.title,
                symptoms=debug_case.symptoms,
                environment=debug_case.environment,
                logs=debug_case.logs,
                tags=debug_case.tags,
                synthetic=debug_case.synthetic,
            )
        )
    except IngestionQueueUnavailableError as exc:
        raise _queue_unavailable_http_error() from exc
    get_logger(__name__, component="api.routes").info(
        "ingestion.queued",
        kind=job.kind,
        job_id=job.job_id,
        record_id=str(job.id),
    )
    metrics_registry.record_ingestion_enqueue_success(job.kind)
    return debug_case


@router.get(
    "/debug-cases/{case_id}",
    response_model=DebugCase,
    dependencies=[Depends(require_api_key)],
)
def get_debug_case(request: Request, case_id: UUID) -> DebugCase:
    with request.app.state.runtime.session_factory() as session:
        repository = KnowledgeRecordRepository(session)
        record = repository.get(case_id)
    if record is None or not _is_debug_case_record(record):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Debug case '{case_id}' was not found.",
        )
    return _record_to_debug_case(record)


@router.post(
    "/documents",
    response_model=IngestionJobResponse,
    dependencies=[Depends(require_api_key)],
)
def ingest_document(payload: DocumentIngestRequest) -> IngestionJobResponse:
    try:
        response = queue_document_ingestion(
            DocumentIngestionJob(
                record_id=uuid4(),
                collection=payload.collection,
                title=payload.title,
                source=payload.source,
                text=payload.text,
                tags=payload.tags,
                synthetic=payload.synthetic,
            )
        )
    except IngestionQueueUnavailableError as exc:
        raise _queue_unavailable_http_error() from exc
    get_logger(__name__, component="api.routes").info(
        "ingestion.queued",
        kind=response.kind,
        job_id=response.job_id,
        record_id=str(response.id),
    )
    metrics_registry.record_ingestion_enqueue_success(response.kind)
    return response


@router.post(
    "/logs/ingest",
    response_model=IngestionJobResponse,
    dependencies=[Depends(require_api_key)],
)
def ingest_log(payload: LogIngestRequest) -> IngestionJobResponse:
    try:
        response = queue_log_ingestion(
            LogIngestionJob(
                record_id=uuid4(),
                service=payload.service,
                raw_message=payload.raw_message,
                severity=payload.severity,
                timestamp=payload.timestamp,
                anomaly_label=payload.anomaly_label,
                source_dataset=payload.source_dataset,
                tags=payload.tags,
            )
        )
    except IngestionQueueUnavailableError as exc:
        raise _queue_unavailable_http_error() from exc
    get_logger(__name__, component="api.routes").info(
        "ingestion.queued",
        kind=response.kind,
        job_id=response.job_id,
        record_id=str(response.id),
    )
    metrics_registry.record_ingestion_enqueue_success(response.kind)
    return response


@router.get(
    "/ingestion-jobs/{job_id}",
    response_model=IngestionJobStatusResponse,
    dependencies=[Depends(require_api_key)],
)
def get_ingestion_job(job_id: str) -> IngestionJobStatusResponse:
    try:
        return get_ingestion_job_status(job_id)
    except IngestionQueueUnavailableError as exc:
        raise _queue_unavailable_http_error() from exc


@router.post("/query", response_model=QueryResponse)
def query(request: Request, payload: QueryRequest) -> QueryResponse:
    with request.app.state.runtime.session_factory() as session:
        response = assistant.answer(payload, DatabaseRetriever(session))
    metrics_registry.record_query(
        latency_ms=response.latency_ms,
        citations_count=len(response.citations),
        confidence=response.confidence,
    )
    get_logger(__name__, component="api.routes").info(
        "query.completed",
        top_k=payload.top_k,
        collections=payload.collections,
        citations_count=len(response.citations),
        warnings_count=len(response.warnings),
        confidence=response.confidence,
        latency_ms=response.latency_ms,
        retrieval_trace_id=str(response.retrieval_trace_id),
    )
    return response


@router.post(
    "/evaluations/run",
    response_model=EvaluationRunResponse,
    dependencies=[Depends(require_api_key)],
)
def evaluation_run(request: Request) -> EvaluationRunResponse:
    with request.app.state.runtime.session_factory() as session:
        response = run_evaluation(DatabaseRetriever(session))
    metrics_registry.record_evaluation(
        passed=response.passed,
        weak_evidence_case_warning_rate=response.weak_evidence_case_warning_rate,
        no_evidence_case_warning_rate=response.no_evidence_case_warning_rate,
    )
    get_logger(__name__, component="api.routes").info(
        "evaluation.completed",
        passed=response.passed,
        cases_evaluated=response.cases_evaluated,
        failures_count=len(response.failures),
        mean_retrieval_score=response.mean_retrieval_score,
        groundedness_pass_rate=response.groundedness_pass_rate,
        citation_presence_rate=response.citation_presence_rate,
        mean_latency_ms=response.mean_latency_ms,
    )
    return response


def _debug_case_record(debug_case: DebugCase) -> KnowledgeRecord:
    return KnowledgeRecord(
        id=debug_case.id,
        collection="incident_cases",
        title=debug_case.title,
        source=_debug_case_source(debug_case.id),
        text=" ".join([debug_case.title, *debug_case.symptoms, *debug_case.logs]),
        tags=tuple(debug_case.tags),
        metadata={
            "kind": "debug_case",
            "synthetic": debug_case.synthetic,
            "symptoms": debug_case.symptoms,
            "environment": debug_case.environment,
            "logs": debug_case.logs,
            "tags": debug_case.tags,
        },
    )


def _record_to_debug_case(record: KnowledgeRecord) -> DebugCase:
    return DebugCase(
        id=record.id,
        title=record.title,
        symptoms=list(record.metadata.get("symptoms", [])),
        environment=dict(record.metadata.get("environment", {})),
        logs=list(record.metadata.get("logs", [])),
        tags=list(record.metadata.get("tags", record.tags)),
        synthetic=bool(record.metadata.get("synthetic", True)),
    )


def _is_debug_case_record(record: KnowledgeRecord) -> bool:
    return record.metadata.get("kind") == "debug_case" and record.source == _debug_case_source(
        record.id
    )


def _debug_case_source(case_id: UUID) -> str:
    return f"synthetic://debug-case/{case_id}"


def _queue_unavailable_http_error() -> HTTPException:
    get_logger(__name__, component="api.routes").warning("ingestion.queue_unavailable")
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error": "queue_unavailable",
            "message": "The ingestion queue is currently unavailable.",
        },
    )


def _runtime_ready(request: Request) -> bool:
    return hasattr(request.app.state, "runtime")


def _database_ready(request: Request) -> bool:
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        return False
    try:
        with runtime.session_factory() as session:
            session.execute(text("SELECT 1"))
    except Exception:
        return False
    return True


def _queue_ready() -> bool:
    try:
        return bool(Redis.from_url(settings.redis_url).ping())
    except RedisError:
        return False
