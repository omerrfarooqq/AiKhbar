"""Application configuration.

All settings are loaded from environment variables (.env) via pydantic-settings.
This is the single source of truth for runtime configuration.
"""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve the .env location independently of the current working directory, so
# the backend loads the same config whether it is started from the repo root or
# from the backend/ directory. A repo-root .env takes priority over a
# backend-local one. In containers, real environment variables still win.
_CONFIG_FILE = Path(__file__).resolve()
_BACKEND_DIR = _CONFIG_FILE.parents[2]
_PROJECT_ROOT = _CONFIG_FILE.parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_BACKEND_DIR / ".env", _PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application ---
    app_name: str = "AiKhbar"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    allowed_origins: str = "http://localhost:5173"

    # --- PostgreSQL ---
    postgres_user: str = "aikhbar"
    postgres_password: str = "aikhbar"
    postgres_db: str = "aikhbar"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str | None = None

    # --- Redis ---
    redis_enabled: bool = False
    redis_url: str = "redis://localhost:6379/0"

    # --- NVIDIA NIM ---
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_llm_model: str = "meta/llama-3.1-70b-instruct"
    nvidia_llm_model_fast: str = "meta/llama-3.1-8b-instruct"
    nvidia_temperature: float = 0.3
    nvidia_max_tokens: int = 2048

    # --- Embeddings / RAG ---
    embedding_model: str = "intfloat/multilingual-e5-base"
    embedding_device: str = "cpu"
    faiss_index_path: str = "./storage/faiss/aikhbar.index"
    faiss_meta_path: str = "./storage/faiss/aikhbar_meta.json"

    # --- TTS ---
    # "Urdu Orator" is Uplift AI's Orator model for Pakistani-language speech.
    tts_primary: Literal["urdu_orator", "coqui"] = "urdu_orator"
    urdu_orator_api_key: str = ""
    urdu_orator_base_url: str = "https://api.upliftai.org/v1"
    urdu_orator_voice_id: str = "v_30s70t3a"
    urdu_orator_output_format: str = "MP3_22050_128"
    coqui_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    audio_cache_dir: str = "./storage/audio"

    # --- Scraping ---
    scraper_user_agent: str = "AiKhbarBot/1.0"
    scrape_interval_minutes: int = 30
    scrape_request_timeout: int = 20
    scrape_max_articles_per_source: int = 40

    # --- Scheduler ---
    scheduler_enabled: bool = True

    # --- Logging ---
    log_level: str = "INFO"
    log_json: bool = False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_url(self) -> str:
        """Async SQLAlchemy connection URL."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — import this everywhere instead of instantiating."""
    return Settings()


settings = get_settings()
