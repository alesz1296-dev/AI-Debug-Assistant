from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.bootstrap import apply_migrations
from app.db.init_db import initialize_database
from app.services.retrieval import DatabaseRetriever, InMemoryRetriever
from app.services.seed_records import seed_knowledge_records


@dataclass
class AppRuntime:
    engine: Engine
    session: Session
    retriever: DatabaseRetriever | InMemoryRetriever
    backend_name: str


def build_runtime(database_url: str | None = None, seed: bool = True) -> AppRuntime:
    url = database_url or settings.database_url
    engine = _build_engine(url)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)()
    if engine.dialect.name == "postgresql":
        apply_migrations(url)
    else:
        initialize_database(engine)
    if seed:
        seed_knowledge_records(session)
    return AppRuntime(
        engine=engine,
        session=session,
        retriever=DatabaseRetriever(session),
        backend_name="postgresql" if engine.dialect.name == "postgresql" else "sqlite",
    )


def _build_engine(database_url: str) -> Engine:
    try:
        engine = create_engine(database_url)
        with engine.connect():
            pass
        return engine
    except SQLAlchemyError:
        if database_url.startswith("sqlite"):
            raise
        return create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
