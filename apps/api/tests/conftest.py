import asyncio
import os
import subprocess
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.main import app as application
from app.core.database import engine, AsyncSessionLocal, get_db
from app.core.config import settings


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Inicializa o banco de dados de teste aplicando todas as migrations do Alembic.
    Roda uma única vez por sessão de teste.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=root_dir,
        capture_output=True,
        text=True,
        env=os.environ
    )
    
    if result.returncode != 0:
        print(f"\n❌ Falha no Alembic Upgrade Head:\n{result.stderr}")
        pytest.exit(f"Database setup failed: {result.stderr}")
    else:
        print("\n✅ Banco de dados de teste inicializado via Alembic.")


@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    """Limpa todas as tabelas antes de cada teste para garantir isolamento."""
    from app.core.database import Base
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Fixture de sessão que força rollback ao final do teste.
    """
    async with engine.connect() as conn:
        await conn.begin()
        async with AsyncSession(bind=conn, expire_on_commit=False) as session:
            yield session
        await conn.rollback()


@pytest_asyncio.fixture(scope="function")
async def app(db_session):
    """
    Override da dependência get_db para que o app use a MESMA sessão do teste.
    Também inicializa o Redis dentro do event loop ativo do teste (fix Bug 1).
    """
    # Bug 1 fix: criar cliente Redis dentro do loop ativo do teste
    tokens_redis = aioredis.from_url(
        f"{settings.REDIS_URL}/{settings.REDIS_TOKENS_DB}",
        decode_responses=True,
    )
    application.state.tokens_redis = tokens_redis
    application.state.queue_redis = aioredis.from_url(
        f"{settings.REDIS_URL}/{settings.REDIS_QUEUE_DB}",
        decode_responses=True,
    )

    async def override_get_db():
        yield db_session
    
    application.dependency_overrides[get_db] = override_get_db
    yield application
    application.dependency_overrides.clear()

    # Fechar os clientes Redis criados para este teste
    await tokens_redis.aclose()
    await application.state.queue_redis.aclose()


@pytest_asyncio.fixture(scope="function")
async def app_own_session():
    """
    Versão do fixture app que usa uma sessão própria por request (não compartilhada).
    Necessário para testes que fazem commit real (ex: register_professional).
    """
    from app.core.database import AsyncSessionLocal

    tokens_redis = aioredis.from_url(
        f"{settings.REDIS_URL}/{settings.REDIS_TOKENS_DB}",
        decode_responses=True,
    )
    application.state.tokens_redis = tokens_redis
    application.state.queue_redis = aioredis.from_url(
        f"{settings.REDIS_URL}/{settings.REDIS_QUEUE_DB}",
        decode_responses=True,
    )

    async def independent_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    application.dependency_overrides[get_db] = independent_get_db
    yield application
    application.dependency_overrides.clear()
    await tokens_redis.aclose()
    await application.state.queue_redis.aclose()


@pytest_asyncio.fixture(scope="function")
async def async_client(app):
    """Cliente HTTP que usa a instância do app com overrides."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def client(async_client):
    """Alias para async_client para compatibilidade."""
    yield async_client


@pytest_asyncio.fixture(autouse=True)
async def dispose_engine():
    """Descarta o pool de conexões após cada teste."""
    yield
    await engine.dispose()
