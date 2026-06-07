"""enable pgvector extension

Revision ID: 0003_enable_vector
Revises: 0002_eval_audit_fields
Create Date: 2026-06-07 00:00:00.000000
"""

from alembic import op

revision = "0003_enable_vector"
down_revision = "0002_eval_audit_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
