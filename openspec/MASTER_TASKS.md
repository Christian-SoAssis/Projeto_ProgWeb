# 🗺️ MASTER TASKS — Ordem de Execução

> **Como usar:** Execute as changes nesta ordem exata. Cada fase depende da anterior.
> Para aplicar uma change: `/opsx:apply` referenciando o nome da change.
> Marque `[x]` quando a change estiver **completamente implementada**.

---

## 🏗️ FASE 1 — INFRAESTRUTURA

> Pré-requisito para tudo. Nenhuma outra fase pode começar sem esta.

### Change: `reduce-containers`
**Caminho:** `openspec/changes/reduce-containers/`
**O que faz:** Consolida a topologia de containers — remove serviços redundantes (Typesense, MinIO, OTEL Collector) e merge do matching no backend principal.

- [x] **Tarefa 1** — Refatoração Backend: mover `apps/matching` → `apps/api/app/matching`, criar `engine.py`, atualizar `requirements.txt`
- [x] **Tarefa 2** — Consolidação PostgreSQL: migração `tsvector`, trigger de atualização, índices `pg_trgm`
- [x] **Tarefa 3** — Docker & Cleanup: atualizar `docker-compose.yml` (4 containers: api, web, postgres, redis), volumes bind mount
- [x] **Tarefa 4** — Verificação: validar matching, busca PostGIS+FTS, upload filesystem, `docker compose up`

**✅ Critério de conclusão:** `docker compose up` sobe com 4 containers e todos os healthchecks passam.

---

### Change: `service-marketplace-platform` — Seção 1 (Fundação)
**Caminho:** `openspec/changes/service-marketplace-platform/`
**O que faz:** Setup completo do monorepo, banco de dados e migrações iniciais.

- [x] **1.1** Configurar monorepo `apps/web` (Next.js 14) + `apps/api` (FastAPI)
- [x] **1.1a** Setup shadcn/ui: `npx shadcn@latest init`, instalar 29 componentes, configurar theme tokens
- [x] **1.2** Docker Compose: PostgreSQL 16 + PostGIS + Redis (4 containers)
- [x] **1.3** Extensões PostgreSQL: PostGIS, pgvector, uuid-ossp
- [x] **1.4** Alembic: init, `env.py` async com SQLAlchemy 2.0
  - [x] **1.4.1–1.4.16** Migrations 001–016 (users, professionals, categories, professional_categories, requests, request_images, bids, contracts, reviews, messages, notifications, disputes, commission_rates, consent_logs, push_subscriptions, favorites)
- [ ] **1.5** Seed: ~20 categorias com hierarquia
- [x] **1.6** Variáveis de ambiente (`.env.example` por app)
- [ ] **1.7** CI básica: lint + type-check + testes (GitHub Actions)
- [ ] **1.8** OpenTelemetry + Grafana dashboard básico
- [x] **1.9** Schema OpenAPI 3.1 auto-gerado via FastAPI
- [ ] **1.10** Frontend consome apenas endpoints documentados (openapi-typescript + lint de contratos)

**✅ Critério de conclusão:** Todas as 16 migrations aplicadas, seed de categorias OK, CI verde.

---

## ⚙️ FASE 2 — BACKEND

> Executar em ordem numérica. Cada seção depende das migrations da Fase 1.

### 2.A — Auth & Cadastro (`service-marketplace-platform` §2)

**TDD obrigatório:** escrever testes ANTES da implementação.

- [x] **2.T1–2.T3** Testes unitários + integração + schemas Pydantic (UserCreate, ProfessionalCreate, LoginRequest, RefreshRequest)
- [x] **2.1** JWT: access token 15min + refresh rotation 7d
- [x] **2.2** `POST /auth/register` com bcrypt
- [x] **2.3** `POST /auth/login`
- [x] **2.4** `POST /auth/refresh` com rotação
- [ ] **2.5** OAuth2 Google: callback + criação/vinculação de conta
- [x] **2.6** `POST /professionals` com upload de documentos (Filesystem Local)
- [x] **2.7** Fluxo de verificação de profissional (`PATCH /admin/professionals/:id`)
- [x] **2.8** Middleware de autenticação/autorização por role
- [x] **2.LT1–2.LT3** Testes LGPD (anonimização, consentimento, exclusão)
- [x] **2.9–2.16** LGPD: consent_logs, endpoints de consentimento, DELETE /auth/me, mascaramento de logs, retenção de dados

### 2.B — Pedidos & VLM (`service-marketplace-platform` §3)

- [ ] **3.T1–3.T3** Testes (geolocalização, urgência, retry, VLM parsing)
- [ ] **3.1** `POST /requests` com geolocalização
- [ ] **3.2** Upload até 5 imagens (Filesystem Local, 10MB cada)
- [ ] **3.3** `GET /requests` (listagem paginada)
- [ ] **3.4** `GET /requests/:id`
- [ ] **3.5** Worker ARQ (Redis) para análise de imagem assíncrona
- [ ] **3.6** Integração Gemini Vision API
- [ ] **3.7** Salvar output VLM (ai_complexity, ai_urgency, ai_specialties)
- [ ] **3.8** Retry com backoff exponencial (3×)
- [ ] **3.9** `GET /categories` (árvore de categorias)

### 2.C — Motor de Matching (`service-marketplace-platform` §4)

- [ ] **4.T1–4.T3** Testes (geo-radius, scoring, fallback v0, schemas)
- [ ] **4.1** `GET /requests/:id/matches` → top-10 profissionais
- [ ] **4.2** Matching v0 por regras: geo-radius + categoria + reputation_score
- [ ] **4.3** Matching Engine LightGBM como módulo `app.matching`
- [ ] **4.4** Integrar no pipeline com timeout 3s + fallback v0
- [ ] **4.5** Coletar dados de treinamento (impressão + conversão)
- [ ] **4.6** Treinar LightGBM v1 com lambdarank
- [ ] **4.7** Re-treino semanal automatizado (cron)
- [ ] **4.8** Log de latência no Grafana

### 2.D — Bids, Contratos & Pagamento (`service-marketplace-platform` §5)

- [ ] **5.T1–5.T3** Testes (bids, contratos, schemas)
- [ ] **5.1** `POST /bids`
- [ ] **5.2** `GET /requests/:id/bids`
- [ ] **5.3** `PATCH /bids/:id` (aceitar/rejeitar)
- [ ] **5.4** Criação automática de contracts ao aceitar bid
- [ ] **5.5** Tabela `commission_rates` + seed taxa padrão 5%
- [ ] **5.6** MercadoPago Marketplace: split-payment com `marketplace_fee`
- [ ] **5.7** `POST /webhooks/mercadopago` (HMAC, idempotência, D+2)
- [ ] **5.8** Job cron de repasse D+2
- [ ] **5.DT1–5.DT3** Testes de disputa
- [ ] **5.9–5.16** Sistema de disputas (abertura, resposta, escalação, resolução, reembolso MercadoPago)

### 2.E — Chat In-App (`service-marketplace-platform` §6)

- [ ] **6.T1–6.T3** Testes (JWT socket, detecção desintermediação, paginação cursor)
- [ ] **6.1** Socket.io no BFF com Redis Adapter
- [ ] **6.2** Autenticação de socket via JWT
- [ ] **6.3** `GET /contracts/:id/messages` (paginação cursor)
- [ ] **6.4** Persistência na tabela `messages`
- [ ] **6.5** Worker NLP para detecção de desintermediação
- [ ] **6.6** Flag de alerta de admin
- [ ] **6.7** Push PWA quando offline / WebSocket quando online

### 2.F — Reviews & Reputação (`service-marketplace-platform` §7)

- [ ] **7.T1–7.T3** Testes (reputation_score, is_authentic, dimensões)
- [ ] **7.1** `POST /reviews` (após pagamento confirmado)
- [ ] **7.2** Worker NLP BERTimbau para scores por dimensão
- [ ] **7.3** Fallback Gemini API
- [ ] **7.4** Detecção de reviews inautênticas
- [ ] **7.5** Recálculo `reputation_score`

### 2.G — Painéis & Busca (Backend) (`service-marketplace-platform` §8–9)

- [ ] **8.T1–8.T3** Testes (métricas, favoritos, notificações)
- [ ] **8.1–8.6** Endpoints: perfil do profissional, métricas, favoritos, painel admin
- [ ] **8.7** Sistema de notificações: WebSocket + push PWA
- [ ] **8.PT1–8.PT3** Testes PWA (Service Worker, cache, schemas)
- [ ] **8.8–8.17** PWA: manifest, Service Worker, cache strategies, offline fallback, push subscriptions, ícones, A2HS
- [ ] **9.T1–9.T3** Testes de busca
- [ ] **9.1–9.4** Busca: PostgreSQL FTS + PostGIS, endpoint `/search/professionals`, trigger FTS, pgvector

---

## 🎨 FASE 3 — FRONTEND

> Todas as changes de UI. Podem ser executadas em paralelo após a Fase 2 expor os endpoints necessários.

> **Pré-requisito compartilhado:** Design system e tokens da `global-visual-identity` devem ser aplicados PRIMEIRO.

### 3.0 — Design System (`global-visual-identity`)
**Caminho:** `openspec/changes/global-visual-identity/`

- [x] **1.1–1.4** Design tokens: DM Sans + DM Mono, cores neomórficas, variáveis CSS, utilitários Tailwind
- [x] **2.1–2.4** Componentes base: Button, Input, NeomorphicCard, Badge
- [ ] **3.1–3.3** Sistema visual de categorias: mapeamento de cores, helper rgba
- [ ] **4.1–4.4** Landing Page hero: Header, Hero, Barra de Busca, Category Pills
- [ ] **5.1–5.3** Landing Page conteúdo: Diferenciais, Grid categorias, Footer
- [ ] **6.1–6.3** Revisão visual e testes de acessibilidade

**✅ Critério:** Tokens e componentes disponíveis globalmente no projeto.

---

### 3.1 — Busca e Descoberta (`search-discovery-screen`)
**Caminho:** `openspec/changes/search-discovery-screen/`
**Depende de:** `GET /search/professionals` (Fase 2.G)

- [ ] **1.1–1.4** Layout split-screen 40/60 (lista + mapa), scroll independente, mobile responsivo
- [ ] **2.1–2.4** Painel de busca: InsetSearchBar, pills de filtro neomórficas, lógica de estado
- [ ] **3.1–3.4** Cards de profissionais: ProfessionalCard, avatar, estatísticas DM Mono, botão ghost
- [ ] **4.1–4.4** Mapa vetorial: provedor (Mapbox), pins por categoria, popup neomórfico, halo pulsante
- [ ] **5.1–5.3** Polimento e testes de performance de mapa

---

### 3.2 — Novo Pedido Etapa 2 (`new-order-step-2`)
**Caminho:** `openspec/changes/new-order-step-2/`
**Depende de:** `POST /requests`, Gemini VLM (Fase 2.B)

- [ ] **1.1–1.3** Stepper neomórfico: 3 etapas, estados visuais, integração na página
- [ ] **2.1–2.4** Formulário: OrderDescriptionCard, UploadArea, TextArea, campos Localização/Urgência
- [ ] **3.1–3.5** Card de Análise IA: barras métricas, badges de categoria, DM Mono
- [ ] **4.1–4.3** Integração CTA: layout combinado, botão "Buscar profissionais", transition loading
- [ ] **5.1–5.3** Revisão visual e testes de UX

---

### 3.3 — Dashboard do Cliente (`client-dashboard-v2`)
**Caminho:** `openspec/changes/client-dashboard-v2/`
**Depende de:** `GET /requests`, `GET /favorites` (Fase 2.G)

- [ ] **1.1–1.3** Layout mobile-first: MobileClientLayout (480px), MobileHeader, badge de notificação
- [ ] **2.1–2.3** NavPills: scroll horizontal, border-radius 50px, estado ativo inset-nm
- [ ] **3.1–3.4** Cards de pedidos: OrderCard elevated-lg, faixa categoria, badges de status, botão ghost
- [ ] **4.1–4.4** Atividade recente: QuickStats 3 mini-cards, valores DM Mono, RecentActivity, separadores
- [ ] **5.1–5.3** Auditoria visual mobile e testes de scroll

---

### 3.4 — Dashboard do Profissional (`professional-dashboard-v2`)
**Caminho:** `openspec/changes/professional-dashboard-v2/`
**Depende de:** `GET /professionals/me/metrics` (Fase 2.G)

- [ ] **1.1–1.4** Layout e Sidebar: ExecutiveSidebar 240px, navegação inset-nm, rodapé com avatar, grid de widgets
- [ ] **2.1–2.4** Stats: StatCard elevated-sm, Ganhos/Lances/Reputação, DM Mono, indicadores variação
- [ ] **3.1–3.4** Gráficos: PerformanceChart, área inset-nm, eixos DM Mono, linha menta
- [ ] **4.1–4.4** Trabalhos e Reputação: lista "Próximos trabalhos", widget reputação granular (4 barras)
- [ ] **5.1–5.3** Polimento e testes de responsividade Desktop

---

### 3.5 — Chat Seguro Mobile (`secure-chat-mobile`)
**Caminho:** `openspec/changes/secure-chat-mobile/`
**Depende de:** Socket.io + `GET /contracts/:id/messages` (Fase 2.E)

- [ ] **1.1–1.3** Header e contexto: SecureChatHeader, avatar com badge de categoria, indicador "Online"
- [ ] **2.1–2.3** Banner de contrato: ContractContextBanner, faixa menta 3px, botão inset
- [ ] **3.1–3.4** Sistema de mensagens: ChatHistory afundado, ReceivedBubble inset-nm, SentBubble elevated-sm, timestamps DM Mono
- [ ] **4.1–4.3** Input e ações: ChatInputBar inset radius-50px, botões de anexo, CTA "Confirmar conclusão"
- [ ] **5.1–5.3** Auditoria visual de sombras e testes mobile

---

### 3.6 — Tela de Configurações & Aparência (`settings-appearance-screen`)
**Caminho:** `openspec/changes/settings-appearance-screen/`

- [ ] **1.1–1.3** Layout e cabeçalho: SettingsLayout elevated-lg, header neomórfico, espaçamento
- [ ] **2.1–2.3** Aparência e Tema: ThemeSegmentedControl, lógica Claro/Escuro, LivePreview
- [ ] **3.1–3.3** Toggles neomórficos: NeomorphicToggle, efeito brilho menta, toggles de notificação
- [ ] **4.1–4.3** Conta e ações: rows de configuração, LogoutButton ghost, cor terracota
- [ ] **5.1–5.3** Revisão visual e testes de transições

---

### 3.7 — Perfil do Profissional (Radar de Reputação) (`service-marketplace-platform` §7.6–7.7)
**Depende de:** `POST /reviews` + scores NLP (Fase 2.F)

- [ ] **7.6** Componente radar de reputação no perfil do profissional
- [ ] **7.7** Exibir scores apenas quando ≥ 3 reviews autênticas

---

### 3.8 — Busca com Mapa (`service-marketplace-platform` §9.5–9.6)
**Depende de:** `GET /search/professionals` + PostGIS (Fase 2.G)

- [ ] **9.5** Página de busca com mapa interativo (Leaflet.js ou Google Maps)
- [ ] **9.6** Clustering de pins para áreas densas

---

## 🚀 FASE 4 — OBSERVABILIDADE & GO-LIVE

**Caminho:** `openspec/changes/service-marketplace-platform/` §10

- [ ] **10.1** OpenTelemetry traces no BFF e workers
- [ ] **10.2** Dashboard Grafana: latência matching, taxa conversão, MAU, GMV
- [ ] **10.3** Testes de carga no matching engine (k6) — alvo: < 80ms p99
- [ ] **10.4** Checklist segurança: OWASP Top 10, rate limiting, sanitização inputs
- [ ] **10.5** Testes E2E do fluxo principal: registro → pedido → match → bid → contrato → pagamento → review
- [ ] **10.6** Deploy em produção: VPS com Docker Compose
- [ ] **10.7** HTTPS, domínio e DNS
- [ ] **10.8** Monitoramento: alertas uptime, CPU/RAM dos containers

---

## 📊 Resumo por Fase

| Fase | Changes | Dependências |
|------|---------|--------------|
| 1 — Infraestrutura | `reduce-containers`, `service-marketplace-platform §1` | Nenhuma |
| 2 — Backend | `service-marketplace-platform §2–9` | Fase 1 completa |
| 3 — Frontend | `global-visual-identity`, `search-discovery-screen`, `new-order-step-2`, `client-dashboard-v2`, `professional-dashboard-v2`, `secure-chat-mobile`, `settings-appearance-screen` | Fase 1 completa; endpoints da Fase 2 conforme indicado |
| 4 — Go-Live | `service-marketplace-platform §10` | Fases 1–3 completas |

> **Nota sobre Fase 3:** As changes de frontend precisam da Fase 1 (monorepo + Docker) e do design system (`global-visual-identity`). Os endpoints específicos necessários estão sinalizados em cada change.
