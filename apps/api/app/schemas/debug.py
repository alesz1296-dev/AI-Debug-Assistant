from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

CollectionName = Literal["incident_cases", "system_logs", "knowledge_base"]


def default_collections() -> list[CollectionName]:
    return ["incident_cases", "system_logs", "knowledge_base"]


class Citation(BaseModel):
    collection: CollectionName
    source: str
    title: str
    snippet: str
    score: float


class DebugCaseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    symptoms: list[str] = Field(min_length=1)
    environment: dict[str, str] = Field(default_factory=dict)
    logs: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    synthetic: bool = True


class DebugCase(BaseModel):
    id: UUID
    title: str
    symptoms: list[str]
    environment: dict[str, str]
    logs: list[str]
    tags: list[str]
    synthetic: bool


class DocumentIngestRequest(BaseModel):
    collection: CollectionName
    title: str = Field(min_length=3, max_length=200)
    source: str = Field(min_length=3)
    text: str = Field(min_length=10)
    tags: list[str] = Field(default_factory=list)
    synthetic: bool = False


class LogIngestRequest(BaseModel):
    service: str
    raw_message: str = Field(min_length=3)
    severity: str = "INFO"
    timestamp: str | None = None
    anomaly_label: str | None = None
    source_dataset: str = "local_demo"
    tags: list[str] = Field(default_factory=list)


class QueryRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    collections: list[CollectionName] = Field(default_factory=default_collections)
    top_k: int = Field(default=5, ge=1, le=15)


class QueryResponse(BaseModel):
    answer: str
    hypotheses: list[str]
    citations: list[Citation]
    confidence: float
    retrieval_trace_id: UUID
    model: str
    latency_ms: int
    warnings: list[str]
    next_steps: list[str]


class EvaluationRunResponse(BaseModel):
    cases_evaluated: int
    mean_retrieval_score: float
    groundedness_pass_rate: float
    citation_presence_rate: float
    mean_latency_ms: float
    weak_evidence_case_warning_rate: float
    no_evidence_case_warning_rate: float
    failures: list[str]
    passed: bool
    thresholds: dict[str, float | int]

