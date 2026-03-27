from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # Ambiente
    ENVIRONMENT: Literal["development", "production"] = "development"
    LOG_LEVEL: str = "debug"

    # Banco de dados
    DATABASE_URL: str = "postgresql+asyncpg://servicoja:servicoja_dev_2026@localhost:5432/servicoja"

    # Redis
    REDIS_URL: str = "redis://:redis_dev_2026@localhost:6379/0"

    # JWT
    JWT_SECRET: str = "jwt_super_secret_dev_key_change_in_production_2026"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Diretórios
    UPLOADS_DIR: str = "./uploads"
    MODELS_DIR: str = "./models"

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
