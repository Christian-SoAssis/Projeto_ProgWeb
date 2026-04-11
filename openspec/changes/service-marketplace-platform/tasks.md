# Tasks: Service Marketplace Platform

## 1. Fundação e Infra

> **Nota:** Módulo 1 concluído. Docker Compose consolidado em 4 containers (db, redis, api, web)
> conforme `reduce-containers`. `apps/db/Dockerfile` customizado resolveu incompatibilidade
> PostGIS + pgvector (base: `postgis/postgis:16-3.4` + pgvector instalado no topo).
> Migrations 001–016 aplicadas. Seed de 16 categorias executado.
> Tasks 1.7, 1.8, 1.9 e 1.10 (CI, OpenTelemetry, OpenAPI export) ficam para o Módulo 10.

- [x] 1.1 Configurar monorepo: pasta `apps/web` (Next.js 14) + `apps/api` (FastAPI + Matching Module)
- [ ] 1.1a Setup shadcn/ui no `apps/web`: `npx shadcn@latest init`, instalar 29 componentes via CLI (`alert`, `alert-dialog`, `avatar`, `badge`, `button`, `calendar`, `card`, `carousel`, `checkbox`, `command`, `dialog`, `dropdown-menu`, `form`, `input`, `label`, `popover`, `progress`, `scroll-area`, `select`, `separator`, `sheet`, `skeleton`, `slider`, `switch`, `table`, `tabs`, `textarea`, `tooltip`, `toast`), configurar theme tokens (cores, fontes), verificar import paths
- [x] 1.2 Configurar Docker Compose: PostgreSQL 16 + PostGIS + Redis (4 containers total)
- [x] 1.3 Instalar extensões PostgreSQL: `PostGIS`, `pgvector`, `uuid-ossp`
- [x] 1.4 Configurar Alembic: `alembic init`, `env.py` async com SQLAlchemy 2.0, `alembic.ini` apontando para `DATABASE_URL`
- [x] 1.4.1 Migration 001: tabela `users` (id, name, email, phone, password_hash, role, avatar_url, is_active, timestamps) + índices
- [x] 1.4.2 Migration 002: tabela `professionals` (FK users ON DELETE CASCADE, bio, location GEOMETRY, service_radius_km, reputation_score, is_verified, profile_embedding vector(1536)) + índices GiST e IVFFlat
- [x] 1.4.3 Migration 003: tabela `categories` (id, name, slug UNIQUE, color VARCHAR(7) DEFAULT '#1a9878', parent_id self-ref ON DELETE SET NULL, sort_order, is_active)
- [x] 1.4.4 Migration 004: tabela `professional_categories` (PK composta, FK professionals + categories ON DELETE CASCADE)
- [x] 1.4.5 Migration 005: tabela `requests` (FK users, FK categories ON DELETE RESTRICT, location GEOMETRY, urgency CHECK, status CHECK, ai_* fields) + índices GiST e compostos
- [x] 1.4.6 Migration 006: tabela `request_images` (FK requests ON DELETE CASCADE, content_type CHECK, size_bytes CHECK ≤ 10MB)
- [x] 1.4.7 Migration 007: tabela `bids` (FK requests + professionals ON DELETE CASCADE, price_cents CHECK > 0, UNIQUE request+professional)
- [x] 1.4.8 Migration 008: tabela `contracts` (FK requests UNIQUE + professionals + users ON DELETE RESTRICT, status CHECK com 7 estados, timestamps de pagamento/repasse)
- [x] 1.4.9 Migration 009: tabela `reviews` (FK contracts UNIQUE ON DELETE RESTRICT, FK users, rating CHECK 1-5, scores NLP CHECK 0-1)
- [x] 1.4.10 Migration 010: tabela `messages` (FK contracts + users ON DELETE CASCADE, content CHECK length ≥ 1) + índice cursor-based
- [x] 1.4.11 Migration 011: tabela `notifications` (FK users ON DELETE CASCADE, type CHECK enum, payload JSONB) + índice parcial não-lidas
- [x] 1.4.12 Migration 012: tabela `disputes` (FK contracts UNIQUE + users ON DELETE RESTRICT, category CHECK enum, status CHECK, resolution CHECK, refund_percent CHECK 1-99) + índice de deadline
- [x] 1.4.13 Migration 013: tabela `commission_rates` (FK categories ON DELETE CASCADE nullable, percent NUMERIC(5,2) CHECK, effective_from/until com validação) + seed taxa padrão 5%
- [x] 1.4.14 Migration 014: tabela `consent_logs` (FK users ON DELETE RESTRICT, consent_type CHECK, ip_address INET, version)
- [x] 1.4.15 Migration 015: tabela `push_subscriptions` (FK users ON DELETE CASCADE, endpoint UNIQUE, keys p256dh/auth)
- [x] 1.4.16 Migration 016: tabela `favorites` (FK users + professionals ON DELETE CASCADE, UNIQUE client+professional)
- [x] 1.5 Seed inicial de categorias: executar script que cria 16 categorias conforme `specs/categories-seed/spec.md` (nome, slug, cor hex, sort_order)
- [x] 1.6 Configurar variáveis de ambiente (`.env.example` para cada app)
- [ ] 1.7 Pipeline CI básica: lint + type-check + testes (GitHub Actions)
- [ ] 1.8 Configurar OpenTelemetry em todos os serviços + Grafana dashboard básico
- [ ] 1.9 Gerar schema OpenAPI 3.1 automaticamente via FastAPI (`/docs` e `/openapi.json`) e exportar artefato versionado no CI
- [ ] 1.10 Validar que o frontend consome apenas endpoints documentados no schema OpenAPI (lint de contratos via `openapi-typescript` + geração de tipos, CI falha se houver chamada a endpoint não documentado)

---

## 2. Auth e Cadastro

### 2.T Testes (TDD — escrever antes da implementação)
- [x] 2.T1 Testes unitários: regras de hash bcrypt, geração/validação de JWT, rotação de refresh token, lógica de roles
- [x] 2.T2 Testes de integração (pytest + httpx): POST /auth/register, POST /auth/login, POST /auth/refresh, POST /professionals, PATCH /admin/professionals/:id — com banco real
- [x] 2.T3 Testes de schema Pydantic (ref: `pydantic-schemas/spec.md` §1, §2, §16):
  - [x] 2.T3a `UserCreate`: name <2 chars, email inválido, phone sem +55, password <8 chars, consent_terms=false, consent_privacy ausente
  - [x] 2.T3b `ProfessionalCreate`: latitude >90, longitude >180, service_radius_km=0, hourly_rate_cents negativo, category_ids vazio/>10, document_type inválido, bio >1000 chars
  - [x] 2.T3c `UserUpdate`: name >100 chars, phone com letras
  - [x] 2.T3d `ProfessionalUpdate`: service_radius_km >200, hourly_rate_cents=0
  - [x] 2.T3e `LoginRequest`: email inválido, password vazio
  - [x] 2.T3f `RefreshRequest`: refresh_token vazio

### 2.I Implementação
- [x] 2.1 Implementar JWT (access token 15min + refresh token rotation 7d)
- [x] 2.2 Endpoint POST /auth/register (cliente) com hash bcrypt
- [x] 2.3 Endpoint POST /auth/login com validação de credenciais
- [x] 2.4 Endpoint POST /auth/refresh com rotação de refresh token
- [ ] 2.5 OAuth2 Google: configurar callback e criação/vinculação de conta
- [x] 2.6 Endpoint POST /professionals para cadastro com upload de documentos para Filesystem Local (StaticFiles)
- [x] 2.7 Fluxo de verificação de profissional: admin aprova via PATCH /admin/professionals/:id
- [x] 2.8 Middleware de autenticação e autorização por role (client, professional, admin)

### 2.L LGPD — Testes (TDD — escrever antes da implementação)
- [x] 2.LT1 Testes unitários: lógica de anonimização de PII (name, email, phone, cpf → valores anônimos), validação de contratos ativos bloqueando exclusão, mascaramento de CPF/CNPJ (regex), sanitização de logs
- [x] 2.LT2 Testes de integração (pytest + httpx): DELETE /auth/me (sucesso, senha errada, contratos ativos), GET /auth/me/consents, validação de consent_logs após registro — com banco real
- [x] 2.LT3 Testes de schema Pydantic (ref: `pydantic-schemas/spec.md` §13, §16):
  - [x] 2.LT3a `DeleteAccountRequest`: password vazio, campo ausente
  - [x] 2.LT3b `ConsentPayload`: consent_terms=false, consent_privacy=false, campos ausentes
  - [x] 2.LT3c `ConsentResponse`: validar from_attributes, campos computed

### 2.L LGPD — Implementação
- [x] 2.9 Criar tabela `consent_logs` (user_id, consent_type, accepted_at, ip_address, user_agent, version) e migration
- [x] 2.10 Adicionar campos `consent_terms` e `consent_privacy` obrigatórios nos schemas de registro (RegisterRequest, ProfessionalCreateRequest); rejeitar cadastro se não aceitos
- [x] 2.11 Endpoint GET /auth/me/consents — listar consentimentos do usuário autenticado
- [x] 2.12 Endpoint DELETE /auth/me — exclusão de conta com confirmação de senha, anonimização de PII, remoção de documentos locais, revogação de tokens, cancelamento de bids pendentes (profissional), atualização de FTS (profissional)
- [x] 2.13 Bloquear exclusão se houver contratos com `status='in_progress'` (retornar `409 Conflict`)
- [x] 2.14 Middleware de mascaramento de logs: CPF (`***.***.***-XX`), CNPJ (`**.***.****/****-XX`), `Authorization: Bearer [REDACTED]`, file paths do S3 omitidos
- [ ] 2.15 SpanProcessor customizado no OpenTelemetry para sanitizar PII nos atributos de spans antes de exportar
- [ ] 2.16 Job de retenção de dados (cron diário): anonimizar contas inativas > 12 meses, remover mensagens de chat > 24 meses, limpar logs com PII > 90 dias; enviar e-mail de aviso 30 dias antes da anonimização

---

## 3. Pedidos de Serviço + Análise de Imagem (VLM)

### 3.T Testes (TDD — escrever antes da implementação)
- [ ] 3.T1 Testes unitários: validação de geolocalização, cálculo de urgência, lógica de retry com backoff, parsing de output VLM (ai_complexity, ai_urgency, ai_specialties)
- [ ] 3.T2 Testes de integração (pytest + httpx): POST /requests, GET /requests, GET /requests/:id, GET /categories — com banco real e upload de imagens mockado
- [ ] 3.T3 Testes de schema Pydantic (ref: `pydantic-schemas/spec.md` §3, §4, §5):
  - [ ] 3.T3a `RequestCreate`: title <5 chars, title >200 chars, description >2000 chars, urgency="urgent", budget_cents=0, latitude >90, category_id inválido
  - [ ] 3.T3b `RequestUpdate`: title <5 chars com campo presente, budget_cents negativo
  - [ ] 3.T3c `CategoryCreate` (admin): slug com espaços/uppercase, name vazio, sort_order negativo
  - [ ] 3.T3d `RequestResponse`/`CategoryResponse`: validar from_attributes, nested relations corretas

### 3.I Implementação
- [ ] 3.1 Endpoint POST /requests com geolocalização e urgência
- [ ] 3.2 Upload de até 5 imagens por pedido (Local Filesystem em `./uploads`, limite 10MB cada)
- [ ] 3.3 Endpoint GET /requests (listagem paginada por cliente)
- [ ] 3.4 Endpoint GET /requests/:id (detalhes do pedido com ai_* fields)
- [ ] 3.5 Configurar worker ARQ (Redis) dentro da API para análise de imagem assíncrona
- [ ] 3.6 Integrar Gemini Vision API no worker com prompt de classificação
- [ ] 3.7 Salvar output VLM nos campos ai_complexity, ai_urgency, ai_specialties
- [ ] 3.8 Implementar retry com backoff exponencial (3× max) para falha na VLM
- [ ] 3.9 Endpoint GET /categories com árvore de categorias

---

## 4. Motor de Matching

### 4.T Testes (TDD — escrever antes da implementação)
- [ ] 4.T1 Testes unitários: cálculo de geo-radius, scoring por categoria + reputation, lógica de fallback v0, ranking top-10
- [ ] 4.T2 Testes de integração (pytest + httpx): GET /requests/:id/matches, teste do matching module em `app.matching` — com banco real e profissionais seed
- [ ] 4.T3 Testes de schema Pydantic (ref: `pydantic-schemas/spec.md`):
  - [ ] 4.T3a `MatchRequest`: request_id inválido, lat/lng fora de range
  - [ ] 4.T3b `ScoreRequest`: features ausentes, tipos errados (string em campo float), campos extra ignorados
  - [ ] 4.T3c `ProfessionalResponse` (nested no match): validar serialização de categories e reputation_score

### 4.I Implementação
- [ ] 4.1 Endpoint GET /requests/:id/matches retornando top-10 profissionais
- [ ] 4.2 Implementar matching v0 por regras: geo-radius + categoria + reputation_score
- [ ] 4.3 Implementar Matching Engine (LightGBM) como módulo interno `app.matching`
- [ ] 4.4 Integrar matching no pipeline de resposta do BFF com timeout 3s + fallback v0
- [ ] 4.5 Coletar dados de treinamento: logs de impressão e conversão
- [ ] 4.6 Treinar modelo LightGBM v1 com lambdarank e substituir matching v0
- [ ] 4.7 Configurar re-treino semanal automatizado (cron job)
- [ ] 4.8 Log de latência do matching no dashboard Grafana

---

## 5. Bids, Contratos e Pagamento

### 5.T Testes (TDD — escrever antes da implementação)
- [ ] 5.T1 Testes unitários: regras de criação de bid (profissional verificado), lógica de aceite/rejeição, criação automática de contract, cálculo de split-payment
- [ ] 5.T2 Testes de integração (pytest + httpx): POST /bids, GET /requests/:id/bids, PATCH /bids/:id — com banco real
- [ ] 5.T3 Testes de schema Pydantic (ref: `pydantic-schemas/spec.md` §6, §7):
  - [ ] 5.T3a `BidCreate`: price_cents=0, price_cents negativo, estimated_hours=0, message >500 chars, request_id inválido, campo ausente
  - [ ] 5.T3b `BidUpdate`: status="pending" (inválido no update), status="cancelled" (inválido)
  - [ ] 5.T3c `ContractResponse`: validar from_attributes, nested professional e dispute

### 5.P Pagamento/Webhook — Testes (TDD — escrever antes da implementação)
- [ ] 5.PT1 Testes unitários: cálculo de `marketplace_fee` com comissão por categoria (5% padrão), fallback para taxa padrão quando categoria sem taxa específica, cálculo de repasse D+2 (dias úteis), lógica de retenção de pagamento em caso de disputa (refund_full/partial/denied)
- [ ] 5.PT2 Testes de integração (pytest + httpx): POST /webhooks/mercadopago (approved, rejected, assinatura inválida, payment_id duplicado/idempotência), POST /contracts/:id/payment (criação de preferência com marketplace_fee correto) — com banco real
- [ ] 5.PT3 Testes de schema Pydantic (ref: `pydantic-schemas/spec.md` §7, §12):
  - [ ] 5.PT3a `PaymentCreate`: validar schema vazio (body-less)
  - [ ] 5.PT3b `WebhookPayload`: campos ausentes, status inválido, payment_id inválido
  - [ ] 5.PT3c `CommissionRateCreate`: percent=0, percent=100, effective_until anterior a effective_from

### 5.I Implementação
- [ ] 5.1 Endpoint POST /bids (profissional verificado envia bid)
- [ ] 5.2 Endpoint GET /requests/:id/bids (cliente visualiza bids recebidos)
- [ ] 5.3 Endpoint PATCH /bids/:id (cliente aceita/rejeita bid)
- [ ] 5.4 Criação automática de contracts ao aceitar bid
- [ ] 5.5 Criar tabela `commission_rates` (category_id nullable, percent, effective_from, effective_until) com seed da taxa padrão de 5%
- [ ] 5.6 Integração MercadoPago Marketplace: split-payment com `marketplace_fee` calculado a partir de `commission_rates`, `collector_id` do profissional
- [ ] 5.7 Endpoint POST /webhooks/mercadopago — validação HMAC, idempotência por `payment_id`, transição para `payment_confirmed`, agendamento de repasse D+2
- [ ] 5.8 Job cron de repasse D+2: liberar pagamento ao profissional se não houver disputa, ou reter se `contract.status='disputed'`
- [ ] 5.9a Notificações (bid_received, bid_accepted, payment_confirmed, payout_completed) via sistema de notificações

### 5.D Disputa — Testes (TDD — escrever antes da implementação)
- [ ] 5.DT1 Testes unitários: lógica de abertura de disputa (cliente ou profissional), cálculo de response_deadline (NOW + 72h), transição de estados (opened → under_review → resolved), lógica de auto_escalation, cálculo de reembolso (total/parcial/negado)
- [ ] 5.DT2 Testes de integração (pytest + httpx): POST /contracts/:id/dispute (cliente e profissional), POST /disputes/:id/response, PATCH /admin/disputes/:id (refund_full, refund_partial, refund_denied), GET /admin/disputes — com banco real
- [ ] 5.DT3 Testes de schema Pydantic (ref: `pydantic-schemas/spec.md` §11):
  - [ ] 5.DT3a `DisputeCreate`: reason <10 chars, reason vazio, category inválida, evidence_urls >10 itens
  - [ ] 5.DT3b `DisputeResponseAction`: message <10 chars, message vazio, evidence_urls >10
  - [ ] 5.DT3c `DisputeResolve`: refund_partial sem refund_percent, refund_full com refund_percent, refund_percent=0, refund_percent=100, admin_notes <5 chars, resolution inválida

### 5.D Disputa — Implementação
- [ ] 5.9 Criar tabela `disputes` (id, contract_id, opened_by, reason, category, evidence_urls, status, resolution, refund_percent, admin_notes, response_deadline, created_at, resolved_at) e migration
- [ ] 5.10 Endpoint POST /contracts/:id/dispute — abertura por cliente ou profissional com `{ reason, category, evidence_urls[] }`, criação de registro com deadline 72h, atualização de contract.status, notificações
- [ ] 5.11 Endpoint POST /disputes/:id/response — parte contrária responde com `{ message, evidence_urls[], proposed_resolution }`, transição para `under_review`, notificações
- [ ] 5.12 Job cron de expiração de disputas: escalar automaticamente disputas sem resposta após 72h (`opened → auto_escalated`), notificar admin e parte não responsiva
- [ ] 5.13 Endpoint PATCH /admin/disputes/:id — admin resolve com `{ resolution: 'refund_full' | 'refund_partial' | 'refund_denied', refund_percent?, admin_notes }`
- [ ] 5.14 Integrar reembolso via MercadoPago API: total (100%), parcial (refund_percent%), ou negado (sem ação financeira); atualizar contract.status correspondente
- [ ] 5.15 Endpoint GET /admin/disputes — listagem paginada com filtro por status, ordenação por created_at
- [ ] 5.16 Notificações em cada transição de estado da disputa (abertura, resposta, escalação, resolução) via WebSocket/push para ambas as partes

---

## 6. Chat In-App

### 6.T Testes (TDD — escrever antes da implementação)
- [ ] 6.T1 Testes unitários: autenticação de socket via JWT, lógica de detecção de desintermediação (regex WhatsApp/telefone/e-mail), persistência de mensagens
- [ ] 6.T2 Testes de integração (pytest + httpx): GET /contracts/:id/messages (paginação com cursor), criação de alertas de admin ao detectar padrão suspeito — com banco real
- [ ] 6.T3 Testes de schema Pydantic (ref: `pydantic-schemas/spec.md` §9):
  - [ ] 6.T3a `MessageCreate`: content vazio, content >5000 chars
  - [ ] 6.T3b `MessageQuery`: limit=0, limit negativo, limit >100, cursor formato inválido
  - [ ] 6.T3c `MessageResponse`: validar from_attributes, sender_name computed

### 6.I Implementação
- [ ] 6.1 Configurar Socket.io no BFF com Redis Adapter para escalonamento horizontal
- [ ] 6.2 Autenticação de socket via JWT
- [ ] 6.3 Endpoint REST GET /contracts/:id/messages para histórico paginado com cursor
- [ ] 6.4 Persistência de mensagens na tabela messages
- [ ] 6.5 Worker NLP para detecção de padrões de desintermediação (WhatsApp, telefone, e-mail externo)
- [ ] 6.6 Criação de flag na tabela de alertas de admin ao detectar padrão suspeito
- [ ] 6.7 Entrega de notificação de nova mensagem via WebSocket se online / push PWA se offline

---

## 7. Reviews e Reputação Granular

### 7.T Testes (TDD — escrever antes da implementação)
- [ ] 7.T1 Testes unitários: cálculo de reputation_score ponderado, lógica de is_authentic, extração de scores por dimensão (pontualidade, qualidade, limpeza, comunicação), regra de >= 3 reviews
- [ ] 7.T2 Testes de integração (pytest + httpx): POST /reviews (apenas após pagamento confirmado), recálculo de reputation_score após insert — com banco real
- [ ] 7.T3 Testes de schema Pydantic (ref: `pydantic-schemas/spec.md` §8):
  - [ ] 7.T3a `ReviewCreate`: rating=0, rating=6, rating negativo, rating float, text <10 chars, text >2000 chars, text vazio, contract_id inválido
  - [ ] 7.T3b `ReviewResponse`: validar from_attributes, score_* entre 0-1, is_authentic default true

### 7.I Implementação
- [ ] 7.1 Endpoint POST /reviews (após pagamento confirmado)
- [ ] 7.2 Worker NLP com BERTimbau para extração de scores por dimensão
- [ ] 7.3 Fallback para Gemini API quando BERTimbau indisponível
- [ ] 7.4 Detecção de reviews inautênticas (is_authentic flag)
- [ ] 7.5 Recálculo de reputation_score do profissional após cada review autêntica
- [ ] 7.6 Componente radar de reputação no perfil do profissional (frontend)
- [ ] 7.7 Exibir scores apenas quando >= 3 reviews autênticas

---

## 8. Painéis e UX

### 8.T Testes (TDD — escrever antes da implementação)
- [ ] 8.T1 Testes unitários: cálculo de métricas (earnings, conversão, reputation), lógica de favoritos, filtros de KPIs admin
- [ ] 8.T2 Testes de integração (pytest + httpx): PATCH /professionals/me, GET /professionals/me/metrics, POST /favorites, GET /favorites — com banco real
- [ ] 8.T3 Testes de schema Pydantic (ref: `pydantic-schemas/spec.md` §10, §15):
  - [ ] 8.T3a `NotificationResponse`: validar from_attributes, type enum, payload dict
  - [ ] 8.T3b `NotificationMarkRead`: notification_ids vazio, >100 itens, UUIDs inválidos
  - [ ] 8.T3c `FavoriteCreate`: professional_id UUID inválido
  - [ ] 8.T3d `ProfessionalUpdate`: validar campos Optional, bio >1000 chars

### 8.I Implementação
- [ ] 8.1 Painel do cliente: pedidos ativos, histórico, bids recebidos, favoritos
- [ ] 8.2 Painel do profissional: agenda, bids pendentes, métricas de earnings e conversão
- [ ] 8.3 Endpoint PATCH /professionals/me para atualização de perfil + atualização `search_vector` (FTS)
- [ ] 8.4 Endpoint GET /professionals/me/metrics (earnings, conversão, reputation)
- [ ] 8.5 Lista de favoritos: POST /favorites e GET /favorites
- [ ] 8.6 Painel admin: aprovação de profissionais, flags de fraude, KPIs gerais
- [ ] 8.7 Sistema de notificações: in-app via WebSocket + push PWA (Service Worker)

### 8.P PWA — Testes (TDD — escrever antes da implementação)
- [ ] 8.PT1 Testes unitários: lógica de seleção de estratégia de cache (cache-first vs network-first por URL pattern), construção do payload de push notification, parsing de manifest.json, detecção de estado online/offline
- [ ] 8.PT2 Testes de integração: Service Worker registration e lifecycle (install → activate → fetch), interceptação de requests com resposta de cache, fallback offline para /pedidos, POST /push/subscribe com subscription válida — via vitest + MSW
- [ ] 8.PT3 Testes de schema (ref: `pydantic-schemas/spec.md` §14):
  - [ ] 8.PT3a `PushSubscribeCreate`: endpoint vazio/<10 chars, keys.p256dh ausente, keys.auth ausente, device_label >100 chars
  - [ ] 8.PT3b `PushKeysSchema`: campos vazios, < 10 chars
  - [ ] 8.PT3c Validação de `manifest.json` contra schema W3C (icons, start_url, display obrigatórios)

### 8.P PWA — Implementação
- [ ] 8.8 Criar `manifest.json` completo (name, short_name, icons 192/512, start_url, display standalone, theme_color, lang pt-BR, categories, screenshots)
- [ ] 8.9 Registrar Service Worker no Next.js (next-pwa ou custom) com pre-cache do app shell no install
- [ ] 8.10 Implementar estratégia Cache-First para assets estáticos (`_next/static/`, fontes, ícones) e cache permanente para imagens locais
- [ ] 8.11 Implementar estratégia Network-First para chamadas de API (`/api/*`) com fallback para cache offline e TTL de 5 min
- [ ] 8.12 Tela de fallback offline para `/pedidos`: banner "Você está offline", dados cacheados da última sync, botões de ação desabilitados, auto-reconexão via evento `online`
- [ ] 8.13 Toast de nova versão do SW: interceptar `updatefound` → exibir "Nova versão disponível — atualize a página"
- [ ] 8.14 Endpoint POST /push/subscribe (backend): salvar subscription (endpoint, keys) vinculada ao user_id e device
- [ ] 8.15 Integrar Web Push API no backend: enviar push para eventos `bid_received`, `new_message`, `dispute_opened` com título, body e deep link; skip se destinatário online no WebSocket
- [ ] 8.16 Gerar ícones PWA (192×192, 512×512) maskable + any, screenshots para install prompt
- [ ] 8.17 Interceptar `beforeinstallprompt` e exibir banner A2HS customizado a partir da segunda visita

---

## 9. Busca e Descoberta

### 9.T Testes (TDD — escrever antes da implementação)
- [ ] 9.T1 Testes unitários: lógica de filtro geo + full-text, cálculo de clustering de pins, construção de query Typesense, geração de embeddings para pgvector
- [ ] 9.T2 Testes de integração (pytest + httpx): GET /search/professionals com combinações de filtros (q, lat/lng, radius_km, category), worker de indexação — com banco real + Typesense
- [ ] 9.T3 Testes de schema Pydantic: inputs inválidos para SearchQuery (radius negativo, coordenadas fora de range, categoria inexistente, paginação inválida)

### 9.I Implementação
- [ ] 9.1 Configurar PostgreSQL FTS e PostGIS para profissionais (nome, bio, categorias, geo, scores)
- [ ] 9.2 Endpoint GET /search/professionals com filtros: q, lat/lng, radius_km, category
- [ ] 9.3 Implementar trigger nativo para atualização do `search_vector`
- [ ] 9.4 Integrar pgvector (embedding de perfil) para busca por similaridade semântica
- [ ] 9.5 Página de busca no frontend com mapa interativo (Leaflet.js ou Google Maps)
- [ ] 9.6 Clustering de pins no mapa para áreas com muitos profissionais

---

## 10. Observabilidade e Go-Live

- [ ] 10.1 OpenTelemetry traces no BFF e workers (OTEL reservado para v2)
- [ ] 10.2 Dashboard Grafana: latência de matching, taxa de conversão, MAU, GMV
- [ ] 10.3 Testes de carga no matching engine (k6) — alvo: < 80ms p99
- [ ] 10.4 Checklist de segurança: OWASP Top 10, rate limiting, sanitização de inputs
- [ ] 10.5 Testes E2E do fluxo principal: registro → pedido → match → bid → contrato → pagamento → review
- [ ] 10.6 Deploy em produção: VPS com Docker Compose (Railway, Render ou VPS próprio)
- [ ] 10.7 Configurar HTTPS, domínio e DNS
- [ ] 10.8 Monitoramento: alertas de uptime, CPU/RAM dos containers
