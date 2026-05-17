"""
AI CFO — Application Configuration

All settings are loaded from environment variables via pydantic-settings.
In production, secrets come from AWS/GCP Secrets Manager, not .env files.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "ai-cfo"
    app_env: str = "development"
    app_debug: bool = False
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://aicfo:aicfo_dev_password@localhost:5432/aicfo"
    database_url_sync: str = "postgresql://aicfo:aicfo_dev_password@localhost:5432/aicfo"

    # ── Redis ────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── JWT Auth ─────────────────────────────────────────────────────────────
    jwt_secret_key: str = "CHANGE-ME-IN-PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── Encryption ───────────────────────────────────────────────────────────
    encryption_key: str = "CHANGE-ME-IN-PRODUCTION"

    # ── Celery ───────────────────────────────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ── Stripe ───────────────────────────────────────────────────────────────
    stripe_test_api_key: str = ""

    # ── Plaid ────────────────────────────────────────────────────────────────
    plaid_client_id: str = ""
    plaid_secret: str = ""
    plaid_env: str = "sandbox"

    # ── Sentry ───────────────────────────────────────────────────────────────
    sentry_dsn: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance. Call this instead of instantiating Settings directly."""
    return Settings()
