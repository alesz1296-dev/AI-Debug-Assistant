from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status

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

router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict[str, str]:
    backend_name = getattr(request.app.state.runtime, "backend_name", "unknown")
    return {
        "status": "ok",
        "service": "enterprise-ai-debug-assistant",
        "backend": backend_name,
    }


@router.post("/debug-cases", response_model=DebugCase, dependencies=[Depends(require_api_key)])
def create_debug_case(request: Request, payload: DebugCaseCreate) -> DebugCase:
    debug_case = DebugCase(id=uuid4(), **payload.model_dump())
    repository = KnowledgeRecordRepository(request.app.state.runtime.session)
    repository.upsert_by_source(_debug_case_record(debug_case))
    request.app.state.runtime.session.commit()
    try:
        queue_debug_case_ingestion(
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
    return debug_case


@router.get(
    "/debug-cases/{case_id}",
    response_model=DebugCase,
    dependencies=[Depends(require_api_key)],
)
def get_debug_case(request: Request, case_id: UUID) -> DebugCase:
    repository = KnowledgeRecordRepository(request.app.state.runtime.session)
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
        return queue_document_ingestion(
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


@router.post(
    "/logs/ingest",
    response_model=IngestionJobResponse,
    dependencies=[Depends(require_api_key)],
)
def ingest_log(payload: LogIngestRequest) -> IngestionJobResponse:
    try:
        return queue_log_ingestion(
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
def query(payload: QueryRequest) -> QueryResponse:
    return assistant.answer(payload)


@router.post(
    "/evaluations/run",
    response_model=EvaluationRunResponse,
    dependencies=[Depends(require_api_key)],
)
def evaluation_run() -> EvaluationRunResponse:
    return run_evaluation()


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
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error": "queue_unavailable",
            "message": "The ingestion queue is currently unavailable.",
        },
    )
