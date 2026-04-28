# 🗺️ MASTER TASKS — Ordem de Execução

> **Como usar:** Esta é a fonte única de verdade para o progresso do projeto. 
> Execute as tarefas na ordem sugerida. Cada fase depende da infraestutura da anterior.
> Marque `[x]` quando a tarefa for **validada**.

---

## 🏗️ FASE 1 — INFRAESTRUTURA

### 1.1 Consolidação de Containers (`reduce-containers`)
*Change: `openspec/changes/reduce-containers/`*
- [x] **1.1.1** Mover `./apps/matching` → `./apps/api/app/matching` + `engine.py`
- [x] **1.1.2** PostgreSQL: migração `tsvector`, trigger de atualização, índices `pg_trgm`
- [x] **1.1.3** Docker Compose: Consolidação em 4 containers (db, redis, api, web)
- [x] **1.1.4** Verificação: healthchecks, matching unitario e PostGIS+FTS

### 1.2 Fundação do Monorepo (`service-marketplace-platform`)
*Change: `openspec/changes/service-marketplace-platform/` §1*
- [x] **1.2.1** Setup `apps/web` (Next.js 14) + `apps/api` (FastAPI)
- [x] **1.2.2** Setup shadcn/ui: instalar 29 componentes e configurar theme tokens
- [x] **1.2.3** Banco de dados: Migrations 001–016 (Completo)
- [x] **1.2.4** Seed inicial de 16 categorias
- [x] **1.2.5** CI básica: lint + type-check + testes (GitHub Actions)
- [x] **1.2.6** Observabilidade: OpenTelemetry + Grafana básico
- [x] **1.2.7** OpenAPI: Geração automática e validação de schema

---

## ⚙️ FASE 2 — BACKEND (Auth, Pedidos, Matching, Pagamentos)

### 2.A — Autenticação, Cadastro e LGPD
*Change: `openspec/changes/service-marketplace-platform/` §2*
- [x] **2.T1** Testes unitários: bcrypt, JWT, refresh rotation, roles logic
- [x] **2.T2** Testes de integração: endpoints `/auth/*`, `/professionals`, admin
- [x] **2.T3** Testes de schema Pydantic (User, Professional, Login, Refresh)
- [x] **2.LT1** Testes LGPD: anonimização, mascaramento de logs, exclusão
- [x] **2.1** JWT: access token 15min + refresh rotation (Redis)
- [x] **2.2** Endpoint `POST /auth/register` (cliente) com hash bcrypt
- [x] **2.3** Endpoint `POST /auth/login`
- [x] **2.4** Endpoint `POST /auth/refresh`
- [x] **2.5** OAuth2 Google: configurar callback e vinculação
- [x] **2.6** Endpoint `POST /professionals` (upload de documentos)
- [x] **2.7** Admin: Fluxo de verificação (`PATCH /admin/professionals/:id`)
- [x] **2.8** Middleware: RBAC (client, professional, admin)
- [x] **2.9** Tabela `consent_logs` + logs de consentimento no registro
- [x] **2.12** Endpoint `DELETE /auth/me` (exclusão com anonimização PII)
- [x] **2.13** Regra: bloqueio de exclusão com contratos ativos
- [x] **2.14** Middleware de mascaramento de logs (CPF, CNPJ, Tokens)
- [ ] **2.15** SpanProcessor OTEL para sanitização de PII
- [ ] **2.16** Job de retenção de dados (cron diário)

### 2.B — Pedidos e Análise de IA (VLM)
*Change: `openspec/changes/service-marketplace-platform/` §3*
- [x] **3.1** Testes: geolocalização, urgência, VLM parsing
- [x] **3.2** Endpoint `POST /requests` com suporte a geolocalização
- [x] **3.3** Upload de múltiplas imagens (Filesystem Local, limite 10MB)
- [x] **3.4** GET Endpoints: Listagem paginada e detalhes do pedido
- [x] **3.5** Integração Gemini Vision (Worker ARQ/Redis)
- [x] **3.6** Parsing IA: `ai_complexity`, `ai_urgency`, `ai_specialties`

### 2.C — Motor de Matching (IA & Regras)
*Change: `openspec/changes/service-marketplace-platform/` §4*
- [x] **4.1** Endpoint `GET /requests/:id/matches` (Matching v0: geo-radius)
- [ ] **4.2** Matching v1: LightGBM lambdarank (módulo `app.matching`)
- [ ] **4.3** Feedback loop: Coleta de dados de impressão e conversão

### 2.D — Transações e Pagamentos (MercadoPago)
*Change: `openspec/changes/service-marketplace-platform/` §5*
- [x] **5.1** Bids: Envio, listagem por cliente e aceite/rejeição
- [x] **5.2** Contratos: Criação automática pós-aceite de bid
- [ ] **5.3** Pagamentos: Split-payment com taxa variável por categoria
- [ ] **5.4** Webhook: Validação HMAC e repasse D+2
- [ ] **5.5** Disputas: Abertura, resposta, escalação e estorno financeiro

### 2.F — Reviews & Reputação (IA NLP)
- [x] **6.1** Modelos: Tabela `reviews` com scores por dimensão
- [x] **6.2** Endpoint `POST /reviews` (pós-contrato completed)
- [x] **6.3** NLP Gemini: Extração de scores (pontualidade, qualidade, etc)
- [x] **6.4** Reputation: Recálculo de core ponderado do profissional
- [x] **6.5** Detecção de Fraude: Heurísticas de reviews inautênticas

### 2.G — Painéis & Busca (TDD)
- [x] **7.1** Busca profissional: Geo-radius + FTS integration
- [x] **7.2** Perfil Profissional: Dashboards de métricas e conversão
- [x] **7.3** Favoritos: Sistema de bookmarking para clientes
- [x] **7.4** Notificações: Fluxo de leitura e listagem de alertas

---

## 🎨 FASE 3 — FRONTEND & UX

### 3.0 — Design System Neomórfico (`global-visual-identity`)
*Change: `openspec/changes/global-visual-identity/`*
- [x] **3.0.1** Tokens: DM Sans + Mono, cores nm, utilitários `elevated` / `inset`
- [x] **3.0.2** Componentes: Button, Input, NeomorphicCard, Badge customizados
- [ ] **3.0.3** Landing Page: Hero, Busca afundada, Category Pills neomórficas
- [ ] **3.0.4** Acessibilidade: Contraste Modo Claro e responsividade de sombras

### 3.1 — Experiência do Usuário (Dashboards & Busca)
- [ ] **3.1.1** Busca split-screen (lista + mapa) (`search-discovery-screen`)
- [ ] **3.1.2** Novo Pedido Stepper com visual IA (`new-order-step-2`)
- [ ] **3.1.3** Client Dash Mobile-first (`client-dashboard-v2`)
- [ ] **3.1.4** Professional Dash Executive grid (`professional-dashboard-v2`)
- [ ] **3.1.5** Chat Seguro Mobile WebSocket (`secure-chat-mobile`)

---

## 🚀 FASE 4 — OBSERVABILIDADE & GO-LIVE
- [ ] **10.1** Traces OpenTelemetry e Dashboard Grafana Final
- [ ] **10.2** k6 Performance Tests (< 80ms p99 matching)
- [ ] **10.3** Deploy Final: VPS + Docker Compose + HTTPS/DNS
