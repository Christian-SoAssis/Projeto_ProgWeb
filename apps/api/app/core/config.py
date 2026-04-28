from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # Ambiente
    ENVIRONMENT: Literal["development", "production"] = "development"
    LOG_LEVEL: str = "debug"

    # Banco de dados
    DATABASE_URL: str = "postgresql+asyncpg://servicoja:servicoja_dev_2026@localhost:5432/servicoja"

    # Redis
    REDIS_URL: str = "redis://:redis_dev_2026@localhost:6379"
    REDIS_TOKENS_DB: int = 1
    REDIS_QUEUE_DB: int = 0

    # JWT
    JWT_SECRET: str = "jwt_super_secret_dev_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LGPD
    TERMS_VERSION: str = "2026-01"

    # Diretórios
    UPLOADS_DIR: str = "./uploads"
    MODELS_DIR: str = "./models"

    # AI
    GOOGLE_API_KEY: str = "[ENCRYPTION_KEY]"
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # OAuth2 Google
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    FRONTEND_AUTH_CALLBACK_URL: str = "http://localhost:3000/auth/callback"

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
