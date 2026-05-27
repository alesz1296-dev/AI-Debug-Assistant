from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import RecordEmbeddingRow


class RecordEmbeddingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(
        self,
        record_id: UUID,
        vector: list[float],
        provider: str,
        model: str,
    ) -> None:
        row = self.session.scalar(
            select(RecordEmbeddingRow).where(
                RecordEmbeddingRow.record_id == str(record_id),
                RecordEmbeddingRow.provider == provider,
                RecordEmbeddingRow.model == model,
            )
        )
        if row is None:
            self.session.add(
                RecordEmbeddingRow(
                    record_id=str(record_id),
                    provider=provider,
                    model=model,
                    dimensions=len(vector),
                    vector=vector,
                )
            )
        else:
            row.dimensions = len(vector)
            row.vector = vector
        self.session.flush()

    def get_vector(self, record_id: UUID, provider: str, model: str) -> list[float] | None:
        row = self.session.scalar(
            select(RecordEmbeddingRow).where(
                RecordEmbeddingRow.record_id == str(record_id),
                RecordEmbeddingRow.provider == provider,
                RecordEmbeddingRow.model == model,
            )
        )
        if row is None:
            return None
        return list(row.vector)

    def count(self) -> int:
        return len(self.session.scalars(select(RecordEmbeddingRow.id)).all())
