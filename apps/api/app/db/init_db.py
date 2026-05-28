from sqlalchemy.engine import Engine

from app.db.bootstrap import create_fallback_schema


def initialize_database(engine: Engine) -> None:
    create_fallback_schema(engine)
