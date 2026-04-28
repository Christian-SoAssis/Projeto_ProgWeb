from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# Engine assíncrono SQLAlchemy 2.0
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "debug",
    future=True,
)

# Instrumentar o SQLAlchemy com OpenTelemetry (se configurado)
import os
if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    SQLAlchemyInstrumentor().instrument(
        engine=engine.sync_engine,
    )

# Session factory assíncrona
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base declarativa para todos os models
class Base(DeclarativeBase):
    pass


# Dependency de sessão para injeção no FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
