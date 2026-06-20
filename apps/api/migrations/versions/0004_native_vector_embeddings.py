"""store embeddings as native pgvector values

Revision ID: 0004_native_vector_embeddings
Revises: 0003_enable_vector
Create Date: 2026-06-17 00:00:00.000000
"""

from alembic import op

revision = "0004_native_vector_embeddings"
down_revision = "0003_enable_vector"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE record_embeddings
        ALTER COLUMN vector TYPE vector(128)
        USING vector::text::vector(128)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_record_embeddings_vector_hnsw
        ON record_embeddings
        USING hnsw (vector vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_record_embeddings_vector_hnsw")
    op.execute(
        """
        ALTER TABLE record_embeddings
        ALTER COLUMN vector TYPE json
        USING to_json((string_to_array(trim(both '[]' from vector::text), ','))::double precision[])
        """
    )
