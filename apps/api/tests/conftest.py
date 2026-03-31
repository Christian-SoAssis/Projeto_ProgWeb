import asyncio
import os
import subprocess
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import AsyncSessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Inicializa o banco de dados de teste aplicando todas as migrations do Alembic.
    Roda uma única vez por sessão de teste.
    """
    # Diretório raiz para encontrar alembic.ini
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar upgrade head via subprocess
    # Usamos subprocess porque o Alembic (cli) é síncrono por padrão mas
    # configurado para async no env.py, e rodar via subprocess isola o loop.
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=root_dir,
        capture_output=True,
        text=True,
        env=os.environ
    )
    
    if result.returncode != 0:
        print(f"\n❌ Falha no Alembic Upgrade Head:\n{result.stderr}")
        # pytest.exit interrompe a execução imediatamente
        pytest.exit(f"Database setup failed: {result.stderr}")
    else:
        print("\n✅ Banco de dados de teste inicializado via Alembic.")


@pytest.fixture(autouse=True)
async def dispose_engine():
    """
    Descarta o pool de conexões do engine após cada teste.
    Isso evita o RuntimeError: "attached to a different loop" ao usar o motor
    global em testes com loops de evento diferentes (asyncio_mode = auto).
    """
    yield
    from app.core.database import engine
    await engine.dispose()


# event_loop fixture removed - handled by pytest-asyncio auto mode


# ── Cliente HTTP assíncrono ─────────────────────────────────────────────────
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def client(async_client):
    yield async_client


# ── Sessão de banco de dados para testes ──────────────────────────────────
@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
