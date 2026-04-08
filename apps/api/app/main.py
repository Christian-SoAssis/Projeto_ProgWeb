from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.v1 import router as v1_router
from app.middleware.log_sanitizer import LogSanitizerMiddleware
from app.core.redis import create_tokens_redis, create_queue_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown da aplicação (padrão moderno FastAPI 0.95+)."""
    # Criar clientes Redis dentro do event loop ativo
    app.state.tokens_redis = create_tokens_redis()
    app.state.queue_redis = create_queue_redis()
    print(f"🚀 ServiçoJá API iniciada em modo {settings.ENVIRONMENT}")
    yield
    # Fechar conexões Redis ao encerrar
    await app.state.tokens_redis.aclose()
    await app.state.queue_redis.aclose()
    print("👋 ServiçoJá API finalizada")


# Criar instância FastAPI
_app = FastAPI(
    title="ServiçoJá API",
    description="Marketplace de serviços locais com IA",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS — apenas em desenvolvimento
if settings.ENVIRONMENT == "development":
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Servir arquivos estáticos (uploads)
uploads_dir = settings.UPLOADS_DIR
os.makedirs(uploads_dir, exist_ok=True)
_app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Routers
_app.include_router(v1_router, prefix="/api/v1")


@_app.get("/health", tags=["Health"])
async def health():
    """Healthcheck endpoint para Docker e load balancers."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


# Registrar middleware
_app.add_middleware(LogSanitizerMiddleware)

app = _app
