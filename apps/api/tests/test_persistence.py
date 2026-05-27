from app.db.init_db import initialize_database
from app.models.records import KnowledgeRecord
from app.repositories.records import KnowledgeRecordRepository
from app.services.seed_data import SEED_RECORDS
from app.services.seed_records import seed_knowledge_records
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def _session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    initialize_database(engine)
    return Session(engine)


def test_seed_knowledge_records_is_idempotent() -> None:
    session = _session()

    first_count = seed_knowledge_records(session)
    second_count = seed_knowledge_records(session)

    repository = KnowledgeRecordRepository(session)
    assert first_count == len(SEED_RECORDS)
    assert second_count == len(SEED_RECORDS)
    assert repository.count() == len(SEED_RECORDS)


def test_record_persists_and_can_be_loaded_by_id() -> None:
    session = _session()
    repository = KnowledgeRecordRepository(session)
    record = KnowledgeRecord(
        collection="knowledge_base",
        title="Runbook: test persistence",
        source="docs/runbooks/test-persistence.md",
        text="This runbook proves records can be stored and loaded from durable state.",
        tags=("runbook", "test"),
        metadata={"synthetic": True},
    )

    saved = repository.upsert_by_source(record)
    session.commit()
    session.expunge_all()

    loaded = repository.get(saved.id)

    assert loaded is not None
    assert loaded.id == saved.id
    assert loaded.source == record.source
    assert loaded.tags == record.tags
    assert loaded.metadata == record.metadata


def test_seed_records_can_be_listed_by_collection() -> None:
    session = _session()
    seed_knowledge_records(session)
    repository = KnowledgeRecordRepository(session)

    records = repository.list_by_collection("incident_cases")

    assert {record.source for record in records} == {
        "synthetic://incident/queue-backlog-after-deploy",
        "synthetic://incident/database-connection-exhaustion",
    }
