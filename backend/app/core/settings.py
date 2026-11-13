"""Runtime configuration.

Everything is read from environment variables (or a local ``.env`` file). The
attribute names here are our own, but each one is bound to the documented
environment variable via ``validation_alias`` so deployments keep working.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Storage
    db_url: str = Field("sqlite:///./campusbite.db", validation_alias="DATABASE_URL")

    # Auth tokens
    token_secret: str = Field("change-me", validation_alias="JWT_SECRET")
    token_algorithm: str = Field("HS256", validation_alias="JWT_ALGORITHM")
    token_ttl_minutes: int = Field(24 * 60, validation_alias="JWT_EXPIRE_MINUTES")

    # Order insights (OpenAI)
    openai_key: str = Field("", validation_alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", validation_alias="OPENAI_MODEL")
    insights_per_minute: int = Field(5, validation_alias="AI_RATE_LIMIT_PER_MINUTE")

    # HTTP
    cors_origins_raw: str = Field("http://localhost:5173", validation_alias="CORS_ORIGINS")

    # Stale-order watcher
    stale_after_minutes: int = Field(15, validation_alias="REMINDER_THRESHOLD_MINUTES")
    sweep_every_seconds: int = Field(60, validation_alias="REMINDER_INTERVAL_SECONDS")
    run_watcher: bool = Field(True, validation_alias="ENABLE_BACKGROUND_TASKS")

    @property
    def allowed_origins(self) -> list[str]:
        origins = (chunk.strip() for chunk in self.cors_origins_raw.split(","))
        return [origin for origin in origins if origin]


@lru_cache
def load_config() -> AppConfig:
    return AppConfig()
