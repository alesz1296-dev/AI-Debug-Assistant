from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import KnowledgeRecordRow
from app.models.records import KnowledgeRecord
from app.schemas.debug import CollectionName


class KnowledgeRecordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_by_source(self, record: KnowledgeRecord) -> KnowledgeRecord:
        row = self.session.scalar(
            select(KnowledgeRecordRow).where(KnowledgeRecordRow.source == record.source)
        )
        if row is None:
            row = KnowledgeRecordRow(
                id=str(record.id),
                collection=record.collection,
                title=record.title,
                source=record.source,
                text=record.text,
                tags=list(record.tags),
                record_metadata=record.metadata,
            )
            self.session.add(row)
        else:
            row.collection = record.collection
            row.title = record.title
            row.text = record.text
            row.tags = list(record.tags)
            row.record_metadata = record.metadata
        self.session.flush()
        return _row_to_record(row)

    def get(self, record_id: UUID) -> KnowledgeRecord | None:
        row = self.session.get(KnowledgeRecordRow, str(record_id))
        if row is None:
            return None
        return _row_to_record(row)

    def list_by_collection(self, collection: CollectionName) -> list[KnowledgeRecord]:
        rows = self.session.scalars(
            select(KnowledgeRecordRow)
            .where(KnowledgeRecordRow.collection == collection)
            .order_by(KnowledgeRecordRow.created_at)
        ).all()
        return [_row_to_record(row) for row in rows]

    def count(self) -> int:
        return len(self.session.scalars(select(KnowledgeRecordRow.id)).all())


def _row_to_record(row: KnowledgeRecordRow) -> KnowledgeRecord:
    return KnowledgeRecord(
        id=UUID(row.id),
        collection=row.collection,  # type: ignore[arg-type]
        title=row.title,
        source=row.source,
        text=row.text,
        tags=tuple(row.tags),
        metadata=dict(row.record_metadata),
    )
