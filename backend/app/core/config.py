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

    # ---- Redis / Celery ----
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # ---- Qdrant ----
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "kb_chunks"
    # gemini-embedding-001 supports 768, 1536, or 3072 via Matryoshka truncation.
    embedding_dimension: int = 1536

    # ---- LLM (OpenAI-compatible: Groq, Mistral, …) ----
    mistral_api_key: str = "change-me"
    mistral_base_url: str = "https://api.groq.com/openai/v1"
    mistral_default_model: str = "llama-3.3-70b-versatile"
    llm_timeout_seconds: int = 60

    # ---- Gemini (embeddings, OpenAI-compatible) ----
    gemini_api_key: str = "change-me"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_timeout_seconds: int = 60

    # ---- Firebase Auth ----
    firebase_project_id: str | None = None
    # Path to the service-account JSON file (preferred in Docker).
    firebase_credentials_path: str | None = None
    # Inline JSON credentials (alternative to path, useful in CI).
    firebase_credentials_json: str | None = None

    # ---- OAuth providers (legacy - auth is handled by Firebase) ----
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    github_redirect_uri: str | None = None

    # ---- File storage ----
    upload_dir: str = "./uploads"
    max_cv_size_mb: int = 5
    # local | cloudinary - cloudinary requires CLOUDINARY_* below
    cv_storage_backend: Literal["local", "cloudinary"] = "local"
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None
    cloudinary_cv_folder: str = "techmentor/cvs"
    # Use Celery for CV + GitHub background jobs (requires docker compose --profile worker).
    cv_use_celery: bool = False
    cv_processing_stale_seconds: int = 20
    github_processing_stale_seconds: int = 20
    # Optional token to avoid GitHub API rate limits (public: 60 req/h).
    github_api_token: str | None = None

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
        if self.is_production:
            if self.mistral_api_key == "change-me":
                raise ValueError("MISTRAL_API_KEY must be set in production.")
            if self.gemini_api_key == "change-me":
                raise ValueError("GEMINI_API_KEY must be set in production.")
        return self

    # ---- Helpers ------------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def cloudinary_configured(self) -> bool:
        return bool(self.cloudinary_cloud_name and self.cloudinary_api_key and self.cloudinary_api_secret)

    @property
    def use_cloudinary_storage(self) -> bool:
        return self.cv_storage_backend == "cloudinary" and self.cloudinary_configured

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
