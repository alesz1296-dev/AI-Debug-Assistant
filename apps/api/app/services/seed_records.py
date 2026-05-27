from sqlalchemy.orm import Session

from app.repositories.embeddings import RecordEmbeddingRepository
from app.repositories.records import KnowledgeRecordRepository
from app.services.embeddings import LocalEmbeddingModel
from app.services.seed_data import SEED_RECORDS


def seed_knowledge_records(session: Session) -> int:
    embedding_model = LocalEmbeddingModel()
    embedding_repository = RecordEmbeddingRepository(session)
    record_repository = KnowledgeRecordRepository(session)
    seeded = 0
    for record in SEED_RECORDS:
        saved_record = record_repository.upsert_by_source(record)
        embedding_repository.upsert(
            record_id=saved_record.id,
            vector=embedding_model.embed(saved_record.text),
            provider=embedding_model.provider,
            model=embedding_model.model,
        )
        seeded += 1
    session.commit()
    return seeded
