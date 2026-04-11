# 🗺️ MASTER TASKS — Ordem de Execução

> **Como usar:** Esta é a fonte única de verdade para o progresso do projeto.
> Nenhuma mudança deve ser feita fora desta lista. Marque `[x]` quando a tarefa for validada.

---

## 🏗️ FASE 1 — INFRAESTRUTURA

### 1.1 Consolidação de Containers (`reduce-containers`)
- [x] **1.1.1** Mover `./apps/matching` → `./apps/api/app/matching` + `engine.py`
- [x] **1.1.2** PostgreSQL: migração `tsvector`, trigger de atualização, índices `pg_trgm`
- [x] **1.1.3** Docker Compose: Consolidação em 4 containers (db, redis, api, web)
- [x] **1.1.4** Verificação: healthchecks, matching unitario e PostGIS+FTS

### 1.2 Fundação do Monorepo (`service-marketplace-platform`)
- [x] **1.2.1** Setup `apps/web` (Next.js 14) + `apps/api` (FastAPI)
- [ ] **1.2.2** Setup shadcn/ui: instalar 29 componentes e configurar theme tokens
- [x] **1.2.3** Banco de dados: Migrations 001–016 (Completo)
- [x] **1.2.4** Seed inicial de 16 categorias
- [ ] **1.2.5** CI básica: lint + type-check + testes (GitHub Actions)
- [ ] **1.2.6** Observabilidade: OpenTelemetry + Grafana básico
- [x] **1.2.7** OpenAPI: Geração automática e validação de schema

---

## ⚙️ FASE 2 — BACKEND (Auth, Pedidos, Matching, Pagamentos)

### 2.A — Autenticação, Cadastro e LGPD
#### Testes (TDD)
- [x] **2.T1** Testes unitários: bcrypt, JWT, refresh rotation, roles logic
- [x] **2.T2** Testes de integração: endpoints `/auth/*`, `/professionals`, admin
- [x] **2.T3** Testes de schema Pydantic (User, Professional, Login, Refresh)
- [x] **2.LT1** Testes LGPD: anonimização, mascaramento de logs, exclusão

#### Implementação Core
- [x] **2.1** JWT: access token 15min + refresh rotation 7d (implementado via Redis)
- [x] **2.2** Endpoint `POST /auth/register` (cliente) com hash bcrypt
- [x] **2.3** Endpoint `POST /auth/login`
- [x] **2.4** Endpoint `POST /auth/refresh`
- [ ] **2.5** OAuth2 Google: configurar callback e vinculação
- [x] **2.6** Endpoint `POST /professionals` (cadastro com upload de documentos)
- [x] **2.7** Admin: Fluxo de verificação (`PATCH /admin/professionals/:id`)
- [x] **2.8** Middleware: RBAC (client, professional, admin)

#### Implementação LGPD
- [x] **2.9** Tabela `consent_logs` + logs de consentimento no registro
- [x] **2.10** Campos `consent_terms` e `consent_privacy` obrigatórios
- [x] **2.11** Endpoint `GET /auth/me/consents`
- [x] **2.12** Endpoint `DELETE /auth/me` (exclusão com anonimização PII)
- [x] **2.13** Regra: bloqueio de exclusão com contratos ativos
- [x] **2.14** Middleware de mascaramento de logs (CPF, CNPJ, Tokens)
- [ ] **2.15** SpanProcessor OTEL para sanitização de PII
- [ ] **2.16** Job de retenção de dados (cron diário)

### 2.B — Pedidos e Análise de IA (VLM)
- [ ] **3.1** Testes: geolocalização, urgência, VLM parsing
- [ ] **3.2** Endpoint `POST /requests` com suporte a geolocalização
- [ ] **3.3** Upload de múltiplas imagens (Filesystem Local, limite 10MB)
- [ ] **3.4** GET Endpoints: Listagem paginada e detalhes do pedido
- [ ] **3.5** Integração Gemini Vision (Worker ARQ/Redis)
- [ ] **3.6** Parsing IA: `ai_complexity`, `ai_urgency`, `ai_specialties`

### 2.C — Motor de Matching (IA & Regras)
- [ ] **4.1** Endpoint `GET /requests/:id/matches` (Matching v0: geo-radius + categoria)
- [ ] **4.2** Matching v1: LightGBM lambdarank (módulo `app.matching`)
- [ ] **4.3** Feedback loop: Coleta de dados de impressão e conversão

### 2.D — Transações e Pagamentos (MercadoPago)
- [ ] **5.1** Bids: Envio, listagem por cliente e aceite/rejeição
- [ ] **5.2** Contratos: Criação automática pós-aceite de bid
- [ ] **5.3** Pagamentos: Split-payment com taxa variável por categoria
- [ ] **5.4** Webhook: Validação HMAC, idempotência e repasse D+2
- [ ] **5.5** Disputas: Abertura, resposta, escalação e estorno financeiro

---

## 🎨 FASE 3 — FRONTEND & UX

### 3.0 — Design System Neomórfico (`global-visual-identity`)
- [ ] **3.0.1** Tokens: DM Sans + Mono, cores nm, utilitários `elevated` / `inset`
- [ ] **3.0.2** Componentes: Button, Input, NeomorphicCard, Badge customizados
- [ ] **3.0.3** Landing Page: Hero, Busca afundada, Category Pills neomórficas
- [ ] **3.0.4** Acessibilidade: Contraste Modo Claro e responsividade de sombras

### 3.1 — Experiência do Usuário (Dashboards & Busca)
- [ ] **3.1.1** Busca: Layout split-screen 40/60 (lista + mapa interativo)
- [ ] **3.1.2** Novo Pedido: Stepper neomórfico com visual IA
- [ ] **3.1.3** Client Dash: Mobile-first layout, NavPills, Order Cards
- [ ] **3.1.4** Professional Dash: Sidebar executiva, Gráficos de performance, Radar de reputação
- [ ] **3.1.5** Chat Seguro: Histórico paginado, WebSocket, detecção de desintermediação

---

## 🚀 FASE 4 — OBSERVABILIDADE & GO-LIVE
- [ ] **10.1** Traces OpenTelemetry e Dashboard Grafana Final
- [ ] **10.2** k6 Performance Tests (< 80ms p99 matching)
- [ ] **10.3** Segurança: OWASP Top 10, Rate limiting, Sanitização
- [ ] **10.4** Deploy Final: VPS + Docker Compose + HTTPS/DNS
