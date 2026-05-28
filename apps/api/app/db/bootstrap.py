from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Engine

from app.db.base import Base

ROOT_DIR = Path(__file__).resolve().parents[4]


def apply_migrations(database_url: str) -> None:
    config = Config(str(ROOT_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")


def create_fallback_schema(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)
