from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    auth_disabled: bool = False
    max_upload_bytes: int = 50 * 1024 * 1024
    database_url: str = "postgresql+asyncpg://vtu:local-dev-only@localhost:5432/vtu_report_studio"
    redis_url: str = "redis://localhost:6379/0"
    storage_backend: str = "local"
    local_storage_path: str = "./private-storage"


@lru_cache
def get_settings() -> Settings:
    return Settings()
