"""expand evaluation run audit fields

Revision ID: 0002_expand_evaluation_run_audit_fields
Revises: 0001_initial_platform_schema
Create Date: 2026-05-28 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_eval_audit_fields"
down_revision = "0001_initial_platform_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "evaluation_runs",
        sa.Column("citation_presence_rate", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "evaluation_runs",
        sa.Column("mean_latency_ms", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "evaluation_runs",
        sa.Column("weak_evidence_warning_rate", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "evaluation_runs",
        sa.Column("no_evidence_warning_rate", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "evaluation_runs",
        sa.Column("passed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "evaluation_runs",
        sa.Column("thresholds", sa.JSON(), nullable=False, server_default="{}"),
    )

    op.alter_column("evaluation_runs", "citation_presence_rate", server_default=None)
    op.alter_column("evaluation_runs", "mean_latency_ms", server_default=None)
    op.alter_column("evaluation_runs", "weak_evidence_warning_rate", server_default=None)
    op.alter_column("evaluation_runs", "no_evidence_warning_rate", server_default=None)
    op.alter_column("evaluation_runs", "passed", server_default=None)
    op.alter_column("evaluation_runs", "thresholds", server_default=None)


def downgrade() -> None:
    op.drop_column("evaluation_runs", "thresholds")
    op.drop_column("evaluation_runs", "passed")
    op.drop_column("evaluation_runs", "no_evidence_warning_rate")
    op.drop_column("evaluation_runs", "weak_evidence_warning_rate")
    op.drop_column("evaluation_runs", "mean_latency_ms")
    op.drop_column("evaluation_runs", "citation_presence_rate")
