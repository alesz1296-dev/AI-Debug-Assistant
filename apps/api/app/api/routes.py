from uuid import uuid4

from fastapi import APIRouter, Depends

from app.core.security import require_api_key
from app.models.records import KnowledgeRecord
from app.schemas.debug import (
    DebugCase,
    DebugCaseCreate,
    DocumentIngestRequest,
    EvaluationRunResponse,
    LogIngestRequest,
    QueryRequest,
    QueryResponse,
)
from app.services.evaluation import run_evaluation
from app.services.rag import assistant
from app.services.retrieval import retriever

router = APIRouter()

_debug_cases: dict[str, DebugCase] = {}


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "enterprise-ai-debug-assistant"}


@router.post("/debug-cases", response_model=DebugCase, dependencies=[Depends(require_api_key)])
def create_debug_case(payload: DebugCaseCreate) -> DebugCase:
    debug_case = DebugCase(id=uuid4(), **payload.model_dump())
    _debug_cases[str(debug_case.id)] = debug_case
    retriever.add(
        KnowledgeRecord(
            collection="incident_cases",
            title=debug_case.title,
            source=f"synthetic://debug-case/{debug_case.id}",
            text=" ".join([debug_case.title, *debug_case.symptoms, *debug_case.logs]),
            tags=tuple(["synthetic" if debug_case.synthetic else "public", *debug_case.tags]),
            metadata={"environment": debug_case.environment},
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


@router.post("/documents", dependencies=[Depends(require_api_key)])
def ingest_document(payload: DocumentIngestRequest) -> dict[str, str]:
    record = retriever.add(
        KnowledgeRecord(
            collection=payload.collection,
            title=payload.title,
            source=payload.source,
            text=payload.text,
            tags=tuple(payload.tags),
            metadata={"synthetic": payload.synthetic},
        )
    )
    return {"id": str(record.id), "status": "indexed"}


@router.post("/logs/ingest", dependencies=[Depends(require_api_key)])
def ingest_log(payload: LogIngestRequest) -> dict[str, str]:
    record = retriever.add(
        KnowledgeRecord(
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
    )
    return {"id": str(record.id), "status": "indexed"}


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
