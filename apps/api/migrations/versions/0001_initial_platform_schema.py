"""initial platform schema

Revision ID: 0001_initial_platform_schema
Revises: 
Create Date: 2026-05-27 00:00:00.000000
"""

# ruff: noqa: I001

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_platform_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("collection", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("source", sa.String(length=500), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source", name="uq_knowledge_records_source"),
    )
    op.create_index("ix_knowledge_records_collection", "knowledge_records", ["collection"])
    op.create_index("ix_knowledge_records_source", "knowledge_records", ["source"])

    op.create_table(
        "record_embeddings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("record_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False),
        sa.Column("vector", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["record_id"], ["knowledge_records.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("record_id", "provider", "model", name="uq_record_embedding_model"),
    )
    op.create_index("ix_record_embeddings_record_id", "record_embeddings", ["record_id"])

    op.create_table(
        "retrieval_traces",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("collections", sa.JSON(), nullable=False),
        sa.Column("top_k", sa.Integer(), nullable=False),
        sa.Column("embedding_provider", sa.String(length=64), nullable=False),
        sa.Column("embedding_model", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "retrieval_trace_hits",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("trace_id", sa.String(length=36), nullable=False),
        sa.Column("record_id", sa.String(length=36), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["trace_id"], ["retrieval_traces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["record_id"], ["knowledge_records.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("trace_id", "rank", name="uq_retrieval_trace_hit_rank"),
    )
    op.create_index("ix_retrieval_trace_hits_trace_id", "retrieval_trace_hits", ["trace_id"])
    op.create_index("ix_retrieval_trace_hits_record_id", "retrieval_trace_hits", ["record_id"])

    op.create_table(
        "evaluation_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("suite_name", sa.String(length=128), nullable=False),
        sa.Column("cases_evaluated", sa.Integer(), nullable=False),
        sa.Column("mean_retrieval_score", sa.Float(), nullable=False),
        sa.Column("groundedness_pass_rate", sa.Float(), nullable=False),
        sa.Column("failures", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_evaluation_runs_suite_name", "evaluation_runs", ["suite_name"])


def downgrade() -> None:
    op.drop_index("ix_evaluation_runs_suite_name", table_name="evaluation_runs")
    op.drop_table("evaluation_runs")

    op.drop_index("ix_retrieval_trace_hits_record_id", table_name="retrieval_trace_hits")
    op.drop_index("ix_retrieval_trace_hits_trace_id", table_name="retrieval_trace_hits")
    op.drop_table("retrieval_trace_hits")

    op.drop_table("retrieval_traces")

    op.drop_index("ix_record_embeddings_record_id", table_name="record_embeddings")
    op.drop_table("record_embeddings")

    op.drop_index("ix_knowledge_records_source", table_name="knowledge_records")
    op.drop_index("ix_knowledge_records_collection", table_name="knowledge_records")
    op.drop_table("knowledge_records")
