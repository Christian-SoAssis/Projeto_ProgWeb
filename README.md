# 🛠️ ServiçoJá — Marketplace de Serviços Locais

> Plataforma web (PWA) que conecta clientes a profissionais verificados no Brasil, com matching inteligente por IA, análise de imagens e reputação granular.

---

## 🎯 Visão Geral

O ServiçoJá é um marketplace de serviços residenciais e comerciais que se diferencia por três pilares de IA:

| Pilar | Tecnologia | Função |
|-------|-----------|--------|
| **Análise de Imagem** | Gemini Vision (VLM) | Cliente fotografa o problema → IA classifica urgência e especialização |
| **Matching Inteligente** | LightGBM (LTR) | Score multi-critério que melhora com cada contratação |
| **Reputação Granular** | BERTimbau (NLP) | Scores por dimensão: pontualidade, qualidade, limpeza, comunicação |

### Fluxo Principal

```
Pedido → Análise VLM → Matching → Bid → Contrato → Pagamento (PIX/Cartão) → Review
```

---

## 🧱 Stack Técnica

### Backend
- **API**: FastAPI (Python) — type hints completos + Pydantic v2
- **ORM**: SQLAlchemy 2.0 (async) / SQLModel
- **Banco**: PostgreSQL 16 + PostGIS + pgvector
- **Cache/Fila**: Redis + BullMQ
- **Busca**: Typesense (full-text PT-BR + geo-search)
- **Storage**: MinIO (S3-compatible)

### Frontend
- **Framework**: Next.js 14 (App Router) + TypeScript
- **UI**: shadcn/ui + Tailwind CSS
- **PWA**: Service Worker, Web Push API, manifest.json

### IA / ML
- **Imagens**: Google Gemini Vision API
- **NLP Reviews**: BERTimbau (HuggingFace) com fallback Gemini
- **Matching**: LightGBM com LambdaRank (microservice FastAPI)

### Infra
- **Deploy**: Docker + Docker Compose
- **Monitoramento**: OpenTelemetry + Grafana
- **Pagamento**: MercadoPago (split-payment marketplace)
- **E-mail/SMS**: Resend + Twilio

---

## 📁 Estrutura do Projeto

```
Projeto_ProgWeb/
├── openspec/                          # Especificações e planejamento
│   ├── config.yaml                    # Regras globais (stack, TDD, processo)
│   └── changes/
│       └── service-marketplace-platform/
│           ├── proposal.md            # O quê e por quê
│           ├── design.md              # Arquitetura, schema DB, pipelines IA
│           ├── tasks.md               # Checklist de implementação (10 módulos)
│           └── specs/                 # Especificações por domínio
│               ├── user-auth/         # Auth JWT, OAuth2, cadastro
│               ├── bid-contract/      # Bid, contrato, pagamento, disputa
│               ├── lgpd/              # Exclusão de conta, consentimento, retenção
│               ├── pwa/               # Service Worker, offline, push notifications
│               ├── chat-messaging/
│               ├── reviews-reputation/
│               ├── matching-engine/
│               ├── service-request/
│               ├── search-discovery/
│               └── ...
├── apps/                              # (a criar)
│   ├── web/                           # Next.js 14 (frontend)
│   ├── api/                           # Fastify BFF
│   └── matching/                      # FastAPI microservice (Python)
└── docker-compose.yml                 # (a criar)
```

---

## 📋 Módulos de Implementação

| # | Módulo | Descrição |
|---|--------|-----------|
| 1 | **Fundação e Infra** | Monorepo, Docker Compose, migrations, CI, OpenAPI schema |
| 2 | **Auth e Cadastro** | JWT, OAuth2 Google, verificação de profissional, LGPD |
| 3 | **Pedidos + VLM** | Criação de pedido, upload de imagens, análise Gemini Vision |
| 4 | **Motor de Matching** | Matching v0 (regras) → v1 (LightGBM LTR), microservice FastAPI |
| 5 | **Bids e Pagamento** | Bid, contrato, split-payment MercadoPago (5% comissão), disputa |
| 6 | **Chat In-App** | WebSocket (Socket.io), anti-desintermediação NLP |
| 7 | **Reviews e Reputação** | NLP granular (BERTimbau), detecção de reviews inautênticas |
| 8 | **Painéis e PWA** | Dashboards cliente/profissional/admin, Service Worker, push |
| 9 | **Busca e Descoberta** | Typesense geo + full-text, mapa interativo, pgvector |
| 10 | **Observabilidade** | OpenTelemetry, Grafana, testes de carga, segurança OWASP |

> Cada módulo segue **TDD**: sub-tarefas de testes (unitários + integração + schema Pydantic) são escritas **antes** do código de implementação.

---

## 🔒 Conformidade LGPD

- **Exclusão de conta**: `DELETE /auth/me` com anonimização de PII
- **Consentimento**: Log auditável no cadastro (LGPD Art. 8)
- **Retenção de dados**: Job automático com prazos por tipo de dado
- **Mascaramento**: CPF/CNPJ/tokens redacted em logs e OpenTelemetry

---

## 🧪 Estratégia de Testes

| Tipo | Escopo | Framework |
|------|--------|-----------|
| **Unitários** | Lógica de negócio, validators, services | pytest + pytest-asyncio |
| **Integração** | Endpoints com banco real | pytest + httpx (FastAPI TestClient) |
| **Schema** | Inputs inválidos Pydantic | pytest |
| **Contrato** | Comunicação entre serviços | schemathesis / schemas compartilhados |
| **E2E** | Fluxo completo pedido→pagamento→review | k6 + browser tests |
| **Frontend** | Componentes, SW, offline | vitest + @testing-library/react + MSW |

---

## 🚀 Quick Start

```bash
# 1. Clonar o repositório
git clone <repo-url>
cd Projeto_ProgWeb

# 2. Copiar variáveis de ambiente
cp .env.example .env

# 3. Subir a infraestrutura
docker-compose up -d

# 4. Rodar migrations
docker-compose exec api alembic upgrade head

# 5. Seed inicial
docker-compose exec api python scripts/seed_categories.py

# 6. Acessar
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# Typesense: http://localhost:8108
# MinIO Console: http://localhost:9001
```

---

## 📐 Convenções

- **Commits**: Conventional Commits (`feat:`, `fix:`, `chore:`, etc.)
- **Variáveis**: `.env` (nunca hardcoded)
- **Idioma**: PT-BR para mensagens de erro ao usuário final
- **Tasks**: Chunks de no máximo 2 horas
- **Branches**: `feat/<modulo>-<descricao>`, `fix/<descricao>`

---

## 📄 Documentação Detalhada

| Documento | Conteúdo |
|-----------|----------|
| [proposal.md](openspec/changes/service-marketplace-platform/proposal.md) | Motivação, capacidades e impacto |
| [design.md](openspec/changes/service-marketplace-platform/design.md) | Arquitetura, schema DB, pipelines IA, trade-offs |
| [tasks.md](openspec/changes/service-marketplace-platform/tasks.md) | Checklist completo de implementação |
| [config.yaml](openspec/config.yaml) | Regras de stack e processo (TDD, Pydantic, shadcn/ui) |

### Specs por Domínio

| Spec | Escopo |
|------|--------|
| [user-auth](openspec/changes/service-marketplace-platform/specs/user-auth/spec.md) | Cadastro, login, OAuth2, refresh token, aprovação admin |
| [bid-contract](openspec/changes/service-marketplace-platform/specs/bid-contract/spec.md) | Bid, contrato, pagamento split, disputa completa |
| [lgpd](openspec/changes/service-marketplace-platform/specs/lgpd/spec.md) | Exclusão, consentimento, retenção, mascaramento |
| [pwa](openspec/changes/service-marketplace-platform/specs/pwa/spec.md) | Service Worker, offline, push notifications, manifest |

---

## 📝 Licença

A definir.
