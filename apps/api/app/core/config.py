from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise AI Debug Assistant"
    app_env: str = "local"
    api_key: str = "dev-local-key"
    database_url: str = "postgresql+psycopg://debug:debug@localhost:5432/debug_assistant"
    allow_sqlite_fallback: bool = False
    redis_url: str = "redis://localhost:6379/0"
    embedding_provider: str = "local"
    llm_provider: str = "local"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

