from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.logging import get_logger
from app.db.bootstrap import apply_migrations
from app.db.init_db import initialize_database
from app.services.seed_records import seed_knowledge_records


@dataclass
class AppRuntime:
    engine: Engine
    session_factory: sessionmaker[Session]
    backend_name: str


def build_runtime(database_url: str | None = None, seed: bool = True) -> AppRuntime:
    url = database_url or settings.database_url
    engine, fallback_used = _build_engine(url)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    if engine.dialect.name == "postgresql":
        if settings.run_db_migrations:
            apply_migrations(url)
    else:
        initialize_database(engine)
    if seed:
        with session_factory() as session:
            seed_knowledge_records(session)
    return AppRuntime(
        engine=engine,
        session_factory=session_factory,
        backend_name=_backend_name(engine, fallback_used),
    )


def _build_engine(database_url: str) -> tuple[Engine, bool]:
    try:
        engine = create_engine(database_url)
        with engine.connect():
            pass
        return engine, False
    except SQLAlchemyError:
        if database_url.startswith("sqlite"):
            raise
        if not settings.allow_sqlite_fallback:
            raise
        get_logger(__name__, component="runtime").warning(
            "runtime.sqlite_fallback_used",
            configured_backend="postgresql",
            fallback_backend="sqlite",
        )
        return (
            create_engine(
                "sqlite://",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            ),
            True,
        )


def _backend_name(engine: Engine, fallback_used: bool) -> str:
    if fallback_used:
        return "sqlite_fallback"
    if engine.dialect.name == "postgresql":
        return "postgresql"
    return "sqlite"
