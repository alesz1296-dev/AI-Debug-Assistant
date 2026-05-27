from sqlalchemy.orm import Session

from app.repositories.records import KnowledgeRecordRepository
from app.services.seed_data import SEED_RECORDS


def seed_knowledge_records(session: Session) -> int:
    repository = KnowledgeRecordRepository(session)
    seeded = 0
    for record in SEED_RECORDS:
        repository.upsert_by_source(record)
        seeded += 1
    session.commit()
    return seeded
