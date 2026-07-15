from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    app_name: str = "Embroidery Design Catalog"
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://usuario:senha@localhost:5432/catalogo_bordados"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "trocar_por_chave"
    s3_secret_key: str = "trocar_por_segredo"
    s3_bucket: str = "matrizes-bordado"
    s3_region: str = "us-east-1"
    api_public_url: str = "http://localhost:8000"
    frontend_public_url: str = "http://localhost:5173"
    max_upload_size_bytes: int = 50 * 1024 * 1024
    trash_retention_days: int = Field(default=30, ge=1)
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
