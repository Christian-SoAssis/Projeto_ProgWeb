import asyncio
import os
import subprocess
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app as application
from app.core.database import engine, AsyncSessionLocal, get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Inicializa o banco de dados de teste aplicando todas as migrations do Alembic.
    Roda uma única vez por sessão de teste.
    """
    # Diretório raiz para encontrar alembic.ini
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar upgrade head via subprocess
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
    Usa um savepoint/transação para isolamento total.
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
    """
    async def override_get_db():
        yield db_session
    
    application.dependency_overrides[get_db] = override_get_db
    yield application
    application.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(app):
    """Cliente HTTP que usa a instância do app com overrides."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(autouse=True)
async def dispose_engine():
    """Descarta o pool de conexões após cada teste."""
    yield
    await engine.dispose()
