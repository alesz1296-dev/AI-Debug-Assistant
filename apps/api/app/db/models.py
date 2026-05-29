from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


def _json_type() -> JSON:
    return JSON().with_variant(JSONB, "postgresql")


class KnowledgeRecordRow(Base):
    __tablename__ = "knowledge_records"
    __table_args__ = (UniqueConstraint("source", name="uq_knowledge_records_source"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    collection: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    source: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    record_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        _json_type(),
        nullable=False,
        default=dict,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_now,
        onupdate=_now,
    )


class RecordEmbeddingRow(Base):
    __tablename__ = "record_embeddings"
    __table_args__ = (
        UniqueConstraint("record_id", "provider", "model", name="uq_record_embedding_model"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    record_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    vector: Mapped[list[float]] = mapped_column(_json_type(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_now,
        onupdate=_now,
    )


class RetrievalTraceRow(Base):
    __tablename__ = "retrieval_traces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    collections: Mapped[list[str]] = mapped_column(_json_type(), nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_now,
    )


class RetrievalTraceHitRow(Base):
    __tablename__ = "retrieval_trace_hits"
    __table_args__ = (
        UniqueConstraint("trace_id", "rank", name="uq_retrieval_trace_hit_rank"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trace_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("retrieval_traces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    record_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_now,
    )


class EvaluationRunRow(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    suite_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    cases_evaluated: Mapped[int] = mapped_column(Integer, nullable=False)
    mean_retrieval_score: Mapped[float] = mapped_column(Float, nullable=False)
    groundedness_pass_rate: Mapped[float] = mapped_column(Float, nullable=False)
    citation_presence_rate: Mapped[float] = mapped_column(Float, nullable=False)
    mean_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    weak_evidence_warning_rate: Mapped[float] = mapped_column(Float, nullable=False)
    no_evidence_warning_rate: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(nullable=False)
    thresholds: Mapped[dict[str, float | int]] = mapped_column(_json_type(), nullable=False)
    failures: Mapped[list[str]] = mapped_column(_json_type(), nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_now,
    )
