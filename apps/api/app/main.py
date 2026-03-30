from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.v1 import router as v1_router
from app.routers.auth import router as auth_router
from app.routers.professionals import router as professionals_router
from app.middleware.log_sanitizer import LogSanitizerMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown da aplicação (padrão moderno FastAPI 0.95+)."""
    print(f"🚀 ServiçoJá API iniciada em modo {settings.ENVIRONMENT}")
    yield
    print("👋 ServiçoJá API finalizada")


# Criar instância FastAPI
app = FastAPI(
    title="ServiçoJá API",
    description="Marketplace de serviços locais com IA",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS — apenas em desenvolvimento
if settings.ENVIRONMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Servir arquivos estáticos (uploads)
uploads_dir = settings.UPLOADS_DIR
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Routers
app.include_router(v1_router, prefix="/api/v1", tags=["API v1"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(professionals_router, prefix="/api/v1", tags=["professionals"])

# Middlewares LGPD
app.add_middleware(LogSanitizerMiddleware)


@app.get("/health", tags=["Health"])
async def health():
    """Healthcheck endpoint para Docker e load balancers."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }
