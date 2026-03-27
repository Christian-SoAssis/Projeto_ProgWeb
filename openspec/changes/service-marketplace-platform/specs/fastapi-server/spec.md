# Spec: fastapi-server

> Configuração do servidor ASGI (Uvicorn) para o backend FastAPI do ServiçoJá. Define comandos de inicialização, workers, logs e diferenças entre desenvolvimento e produção.

---

## Servidor ASGI

O backend FastAPI **MUST** usar **Uvicorn** como servidor ASGI (Asynchronous Server Gateway Interface).

| Aspecto | Valor |
|---------|-------|
| **Servidor** | Uvicorn 0.30+ |
| **Alternativa de Produção** | Gunicorn + Uvicorn workers |
| **Porta** | 8000 |
| **Host** | `0.0.0.0` (bind all interfaces no container) |
| **Reload** | Ativado em dev, desativado em prod |

---

## Ambiente de Desenvolvimento

### Comando de Inicialização

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --log-level debug
```

**Flags explicadas:**
- `--reload`: Auto-reload quando código muda (apenas dev)
- `--log-level debug`: Logs verbosos para debugging
- `--host 0.0.0.0`: Escuta em todas as interfaces (necessário no Docker)

### Dockerfile (Desenvolvimento)

```dockerfile
FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 8000

# Comando de inicialização (desenvolvimento)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Características Dev

| Item | Valor |
|------|-------|
| **Workers** | 1 (single-process) |
| **Hot-reload** | ✅ Ativado |
| **Log format** | Texto colorido (console-friendly) |
| **Timeout** | Infinito (debug sessions) |

---

## Ambiente de Produção

### Comando de Inicialização (Gunicorn + Uvicorn)

```bash
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --timeout 30 \
  --graceful-timeout 30
```

**Flags explicadas:**
- `-w 4`: 4 workers (regra: 2×CPU cores)
- `-k uvicorn.workers.UvicornWorker`: Worker class do Uvicorn
- `--timeout 30`: Timeout de 30s para requests lentos
- `--graceful-timeout 30`: Tempo para finalizar requests em shutdown

### Dockerfile (Produção)

```dockerfile
FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependências (cache layer separado)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar código
COPY . .

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicialização (produção)
CMD ["gunicorn", "app.main:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--timeout", "30", \
     "--graceful-timeout", "30"]
```

### Características Prod

| Item | Valor |
|------|-------|
| **Workers** | 4 (ou 2×vCPUs do servidor) |
| **Hot-reload** | ❌ Desativado |
| **Log format** | JSON estruturado (via middleware) |
| **Timeout** | 30s |
| **Graceful shutdown** | 30s |
| **User** | `appuser` (non-root) |

---

## Estrutura do main.py

O ponto de entrada da aplicação **MUST** seguir esta estrutura:

```python
# apps/api/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.v1 import router as v1_router
from app.webhooks import router as webhooks_router
from app.core.config import settings

# Criar instância FastAPI
app = FastAPI(
    title="ServiçoJá API",
    description="Marketplace de serviços locais com IA",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS (apenas dev)
if settings.ENVIRONMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Servir arquivos estáticos (uploads)
uploads_dir = os.getenv("UPLOADS_DIR", "./uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Routers
app.include_router(v1_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/webhooks")

# Healthcheck
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Lifespan events (startup/shutdown)
@app.on_event("startup")
async def startup():
    # Inicializar conexões, cache, etc.
    pass

@app.on_event("shutdown")
async def shutdown():
    # Fechar conexões gracefully
    pass
```

> **Nota**: `@app.on_event` será migrado para o padrão `lifespan` context manager de acordo com as boas práticas FastAPI 0.95+. O exemplo acima usa a forma compatível com FastAPI 0.30+.

---

## Logs Estruturados

### Desenvolvimento (Uvicorn)

Logs coloridos no console:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:52345 - "GET /health HTTP/1.1" 200 OK
```

### Produção (Gunicorn + JSON)

Logs JSON estruturados via middleware:

```json
{"timestamp": "2026-03-27T10:00:00Z", "level": "info", "message": "Application startup complete"}
{"timestamp": "2026-03-27T10:00:01Z", "level": "info", "method": "GET", "path": "/health", "status": 200, "duration_ms": 2}
```

---

## Variáveis de Ambiente

| Variável | Dev | Prod | Descrição |
|----------|-----|------|-----------|
| `ENVIRONMENT` | `development` | `production` | Controla CORS, modo debug |
| `PORT` | `8000` | `8000` | Porta de escuta |
| `WORKERS` | `1` | `4` | Número de workers Gunicorn |
| `LOG_LEVEL` | `debug` | `info` | Nível de log |
| `UPLOADS_DIR` | `./uploads` | `/data/uploads` | Diretório de uploads |

---

## Integração com docker-compose.yml

```yaml
# Trecho relevante do docker-compose.yml
services:
  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./apps/api:/app           # Hot-reload em dev
      - ./uploads:/data/uploads   # Persistência de uploads
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```
