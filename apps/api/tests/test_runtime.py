import pytest
from app.core.config import settings
from app.core.runtime import build_runtime
from sqlalchemy.exc import SQLAlchemyError


def test_runtime_requires_explicit_sqlite_fallback() -> None:
    original = settings.allow_sqlite_fallback
    settings.allow_sqlite_fallback = False
    try:
        with pytest.raises(SQLAlchemyError):
            build_runtime(
                "postgresql+psycopg://debug:debug@127.0.0.1:1/debug_assistant?connect_timeout=1"
            )
    finally:
        settings.allow_sqlite_fallback = original


def test_runtime_uses_sqlite_fallback_only_when_enabled() -> None:
    original = settings.allow_sqlite_fallback
    settings.allow_sqlite_fallback = True
    runtime = None
    try:
        runtime = build_runtime(
            "postgresql+psycopg://debug:debug@127.0.0.1:1/debug_assistant?connect_timeout=1",
            seed=False,
        )
        assert runtime.backend_name == "sqlite_fallback"
    finally:
        if runtime is not None:
            runtime.session.close()
            runtime.engine.dispose()
        settings.allow_sqlite_fallback = original
