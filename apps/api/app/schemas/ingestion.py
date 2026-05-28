from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.debug import CollectionName

IngestionJobKind = Literal["document", "log", "debug_case"]
IngestionJobStatus = Literal["queued", "started", "finished", "failed", "not_found"]


class DocumentIngestionJob(BaseModel):
    record_id: UUID
    collection: CollectionName
    title: str = Field(min_length=3, max_length=200)
    source: str = Field(min_length=3)
    text: str = Field(min_length=10)
    tags: list[str] = Field(default_factory=list)
    synthetic: bool = False


class LogIngestionJob(BaseModel):
    record_id: UUID
    service: str
    raw_message: str = Field(min_length=3)
    severity: str = "INFO"
    timestamp: str | None = None
    anomaly_label: str | None = None
    source_dataset: str = "local_demo"
    tags: list[str] = Field(default_factory=list)


class DebugCaseIngestionJob(BaseModel):
    record_id: UUID
    title: str = Field(min_length=3, max_length=200)
    symptoms: list[str] = Field(min_length=1)
    environment: dict[str, str] = Field(default_factory=dict)
    logs: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    synthetic: bool = True


class IngestionJobResponse(BaseModel):
    id: UUID
    job_id: str
    kind: IngestionJobKind
    status: Literal["queued"]


class IngestionJobStatusResponse(BaseModel):
    job_id: str
    kind: IngestionJobKind | None = None
    status: IngestionJobStatus
    result: str | None = None
    error_type: str | None = None
    error_message: str | None = None
