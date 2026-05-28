from uuid import uuid4

from fastapi import APIRouter, Depends

from app.core.security import require_api_key
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
    get_ingestion_job_status,
    queue_debug_case_ingestion,
    queue_document_ingestion,
    queue_log_ingestion,
)
from app.services.rag import assistant

router = APIRouter()

_debug_cases: dict[str, DebugCase] = {}


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "enterprise-ai-debug-assistant"}


@router.post("/debug-cases", response_model=DebugCase, dependencies=[Depends(require_api_key)])
def create_debug_case(payload: DebugCaseCreate) -> DebugCase:
    debug_case = DebugCase(id=uuid4(), **payload.model_dump())
    _debug_cases[str(debug_case.id)] = debug_case
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
    return debug_case


@router.get(
    "/debug-cases/{case_id}",
    response_model=DebugCase,
    dependencies=[Depends(require_api_key)],
)
def get_debug_case(case_id: str) -> DebugCase:
    return _debug_cases[case_id]


@router.post(
    "/documents",
    response_model=IngestionJobResponse,
    dependencies=[Depends(require_api_key)],
)
def ingest_document(payload: DocumentIngestRequest) -> IngestionJobResponse:
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


@router.post(
    "/logs/ingest",
    response_model=IngestionJobResponse,
    dependencies=[Depends(require_api_key)],
)
def ingest_log(payload: LogIngestRequest) -> IngestionJobResponse:
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


@router.get(
    "/ingestion-jobs/{job_id}",
    response_model=IngestionJobStatusResponse,
    dependencies=[Depends(require_api_key)],
)
def get_ingestion_job(job_id: str) -> IngestionJobStatusResponse:
    return get_ingestion_job_status(job_id)


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
