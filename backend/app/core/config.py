"""Centralized application configuration.

All settings are loaded from environment variables (or a local `.env` file)
via `pydantic-settings`. No secrets are hard-coded.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed settings for the whole backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- App ----
    app_name: str = "TechMentor AI"
    app_env: Literal["local", "staging", "production"] = "local"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_v1_prefix: str = "/api/v1"
    frontend_url: AnyHttpUrl = "http://localhost:3000"

    # ---- Security ----
    secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    password_reset_token_expire_hours: int = 1

    # ---- Database ----
    postgres_user: str = "techmentor"
    postgres_password: str = "techmentor"
    postgres_db: str = "techmentor"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    # The app uses the async URL. If unset, it's derived from POSTGRES_* below.
    database_url: str | None = None
    # Sync URL for Alembic. If unset, derived from database_url (asyncpg -> psycopg).
    sync_database_url: str | None = None
    # Force SSL on the DB connection (Neon and most managed PG require this).
    db_ssl_mode: str | None = "require"

    # ---- Redis / Celery ----
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # ---- Qdrant ----
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "kb_chunks"
    embedding_dimension: int = 1536

    # ---- RodiumAI (LLM gateway) ----
    rodium_api_key: str = "change-me"
    rodium_base_url: str = "https://api.rodiumai.io/v1"
    rodium_default_model: str = "mistralai/mistral-small-latest"
    rodium_embedding_model: str = "text-embedding-3-small"
    rodium_timeout_seconds: int = 60

    # ---- Firebase Auth ----
    firebase_project_id: str | None = None
    # Path to the service-account JSON file (preferred in Docker).
    firebase_credentials_path: str | None = None
    # Inline JSON credentials (alternative to path, useful in CI).
    firebase_credentials_json: str | None = None

    # ---- OAuth providers (legacy — auth is handled by Firebase) ----
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    github_redirect_uri: str | None = None

    # ---- File storage ----
    upload_dir: str = "./uploads"
    max_cv_size_mb: int = 5

    # ---- CORS ----
    backend_cors_origins: list[AnyHttpUrl] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    # ---- Validators ---------------------------------------------------
    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def _parse_cors(cls, value: object) -> object:
        if isinstance(value, str) and not value.startswith("["):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value

    @model_validator(mode="after")
    def _build_database_url(self) -> Settings:
        """Derive the async + sync DB URLs from POSTGRES_* if not provided."""
        if not self.database_url:
            self.database_url = (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        if not self.sync_database_url:
            # Alembic uses a synchronous driver. asyncpg -> psycopg (v3).
            self.sync_database_url = self.database_url.replace(
                "postgresql+asyncpg://", "postgresql+psycopg://", 1
            )
        return self

    # ---- Helpers ------------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached `Settings` instance (single source of truth)."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
