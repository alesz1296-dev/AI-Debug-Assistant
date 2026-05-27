from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.db.base import Base


def initialize_database(engine: Engine) -> None:
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
