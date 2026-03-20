# Tasks: Service Marketplace Platform

## 1. Fundação e Infra

- [ ] 1.1 Configurar monorepo: pasta `apps/web` (Next.js 14) + `apps/api` (Fastify) + `apps/matching` (Python FastAPI)
- [ ] 1.2 Configurar Docker Compose: PostgreSQL 16 + PostGIS + Redis + MinIO + Typesense
- [ ] 1.3 Instalar extensões PostgreSQL: `PostGIS`, `pgvector`, `uuid-ossp`
- [ ] 1.4 Executar migrations do schema principal (tabelas do design.md)
- [ ] 1.5 Seed inicial de categorias (~20 categorias com hierarquia)
- [ ] 1.6 Configurar variáveis de ambiente (`.env.example` para cada app)
- [ ] 1.7 Pipeline CI básica: lint + type-check + testes (GitHub Actions)
- [ ] 1.8 Configurar OpenTelemetry em todos os serviços + Grafana dashboard básico
- [ ] 1.9 Gerar schema OpenAPI 3.1 automaticamente via FastAPI (`/docs` e `/openapi.json`) e exportar artefato versionado no CI
- [ ] 1.10 Validar que o frontend consome apenas endpoints documentados no schema OpenAPI (lint de contratos via `openapi-typescript` + geração de tipos, CI falha se houver chamada a endpoint não documentado)

---

## 2. Auth e Cadastro

### 2.T Testes (TDD — escrever antes da implementação)
- [ ] 2.T1 Testes unitários: regras de hash bcrypt, geração/validação de JWT, rotação de refresh token, lógica de roles
- [ ] 2.T2 Testes de integração (pytest + httpx): POST /auth/register, POST /auth/login, POST /auth/refresh, POST /professionals, PATCH /admin/professionals/:id — com banco real
- [ ] 2.T3 Testes de schema Pydantic: inputs inválidos para RegisterRequest, LoginRequest, RefreshRequest, ProfessionalCreateRequest (campos ausentes, tipos errados, e-mail inválido, senha fraca)

### 2.I Implementação
- [ ] 2.1 Implementar JWT (access token 15min + refresh token rotation 7d)
- [ ] 2.2 Endpoint POST /auth/register (cliente) com hash bcrypt
- [ ] 2.3 Endpoint POST /auth/login com validação de credenciais
- [ ] 2.4 Endpoint POST /auth/refresh com rotação de refresh token
- [ ] 2.5 OAuth2 Google: configurar callback e criação/vinculação de conta
- [ ] 2.6 Endpoint POST /professionals para cadastro com upload de documentos para S3/MinIO
- [ ] 2.7 Fluxo de verificação de profissional: admin aprova via PATCH /admin/professionals/:id
- [ ] 2.8 Middleware de autenticação e autorização por role (client, professional, admin)

### 2.L LGPD — Testes (TDD — escrever antes da implementação)
- [ ] 2.LT1 Testes unitários: lógica de anonimização de PII (name, email, phone, cpf → valores anônimos), validação de contratos ativos bloqueando exclusão, mascaramento de CPF/CNPJ (regex), sanitização de logs
- [ ] 2.LT2 Testes de integração (pytest + httpx): DELETE /auth/me (sucesso, senha errada, contratos ativos), GET /auth/me/consents, validação de consent_logs após registro — com banco real
- [ ] 2.LT3 Testes de schema Pydantic: inputs inválidos para DeleteAccountRequest (senha ausente), ConsentPayload (consent_terms=false, campo ausente), verificação de campos mascarados no response

### 2.L LGPD — Implementação
- [ ] 2.9 Criar tabela `consent_logs` (user_id, consent_type, accepted_at, ip_address, user_agent, version) e migration
- [ ] 2.10 Adicionar campos `consent_terms` e `consent_privacy` obrigatórios nos schemas de registro (RegisterRequest, ProfessionalCreateRequest); rejeitar cadastro se não aceitos
- [ ] 2.11 Endpoint GET /auth/me/consents — listar consentimentos do usuário autenticado
- [ ] 2.12 Endpoint DELETE /auth/me — exclusão de conta com confirmação de senha, anonimização de PII, remoção de documentos do S3/MinIO, revogação de tokens, cancelamento de bids pendentes (profissional), remoção do Typesense (profissional)
- [ ] 2.13 Bloquear exclusão se houver contratos com `status='in_progress'` (retornar `409 Conflict`)
- [ ] 2.14 Middleware de mascaramento de logs: CPF (`***.***.***-XX`), CNPJ (`**.***.****/****-XX`), `Authorization: Bearer [REDACTED]`, file paths do S3 omitidos
- [ ] 2.15 SpanProcessor customizado no OpenTelemetry para sanitizar PII nos atributos de spans antes de exportar
- [ ] 2.16 Job de retenção de dados (cron diário): anonimizar contas inativas > 12 meses, remover mensagens de chat > 24 meses, limpar logs com PII > 90 dias; enviar e-mail de aviso 30 dias antes da anonimização

---

## 3. Pedidos de Serviço + Análise de Imagem (VLM)

### 3.T Testes (TDD — escrever antes da implementação)
- [ ] 3.T1 Testes unitários: validação de geolocalização, cálculo de urgência, lógica de retry com backoff, parsing de output VLM (ai_complexity, ai_urgency, ai_specialties)
- [ ] 3.T2 Testes de integração (pytest + httpx): POST /requests, GET /requests, GET /requests/:id, GET /categories — com banco real e upload de imagens mockado
- [ ] 3.T3 Testes de schema Pydantic: inputs inválidos para ServiceRequestCreate (coordenadas fora de range, urgência inválida, campos ausentes, imagens acima do limite)

### 3.I Implementação
- [ ] 3.1 Endpoint POST /requests com geolocalização e urgência
- [ ] 3.2 Upload de até 5 imagens por pedido (S3/MinIO, limite 10MB cada)
- [ ] 3.3 Endpoint GET /requests (listagem paginada por cliente)
- [ ] 3.4 Endpoint GET /requests/:id (detalhes do pedido com ai_* fields)
- [ ] 3.5 Configurar worker BullMQ para análise de imagem assíncrona
- [ ] 3.6 Integrar Gemini Vision API no worker com prompt de classificação
- [ ] 3.7 Salvar output VLM nos campos ai_complexity, ai_urgency, ai_specialties
- [ ] 3.8 Implementar retry com backoff exponencial (3× max) para falha na VLM
- [ ] 3.9 Endpoint GET /categories com árvore de categorias

---

## 4. Motor de Matching

### 4.T Testes (TDD — escrever antes da implementação)
- [ ] 4.T1 Testes unitários: cálculo de geo-radius, scoring por categoria + reputation, lógica de fallback v0, ranking top-10
- [ ] 4.T2 Testes de integração (pytest + httpx): GET /requests/:id/matches, POST /score (microservice FastAPI) — com banco real e profissionais seed
- [ ] 4.T3 Testes de schema Pydantic: inputs inválidos para MatchRequest, ScoreRequest (features ausentes, tipos errados, lat/lng inválidos)

### 4.I Implementação
- [ ] 4.1 Endpoint GET /requests/:id/matches retornando top-10 profissionais
- [ ] 4.2 Implementar matching v0 por regras: geo-radius + categoria + reputation_score
- [ ] 4.3 Microservice Python (FastAPI): endpoint POST /score com features LightGBM
- [ ] 4.4 Integrar microservice de matching no BFF com timeout 3s + fallback v0
- [ ] 4.5 Coletar dados de treinamento: logs de impressão e conversão
- [ ] 4.6 Treinar modelo LightGBM v1 com lambdarank e substituir matching v0
- [ ] 4.7 Configurar re-treino semanal automatizado (cron job)
- [ ] 4.8 Log de latência do matching no dashboard Grafana

---

## 5. Bids, Contratos e Pagamento

### 5.T Testes (TDD — escrever antes da implementação)
- [ ] 5.T1 Testes unitários: regras de criação de bid (profissional verificado), lógica de aceite/rejeição, criação automática de contract, cálculo de split-payment
- [ ] 5.T2 Testes de integração (pytest + httpx): POST /bids, GET /requests/:id/bids, PATCH /bids/:id — com banco real
- [ ] 5.T3 Testes de schema Pydantic: inputs inválidos para BidCreate, BidUpdate (valores negativos, status inválido, campos ausentes)

### 5.P Pagamento/Webhook — Testes (TDD — escrever antes da implementação)
- [ ] 5.PT1 Testes unitários: cálculo de `marketplace_fee` com comissão por categoria (5% padrão), fallback para taxa padrão quando categoria sem taxa específica, cálculo de repasse D+2 (dias úteis), lógica de retenção de pagamento em caso de disputa (refund_full/partial/denied)
- [ ] 5.PT2 Testes de integração (pytest + httpx): POST /webhooks/mercadopago (approved, rejected, assinatura inválida, payment_id duplicado/idempotência), POST /contracts/:id/payment (criação de preferência com marketplace_fee correto) — com banco real
- [ ] 5.PT3 Testes de schema Pydantic: inputs inválidos para PaymentCreate (contract_id inexistente), WebhookPayload (campos ausentes, status inválido), validação de `X-Signature` HMAC

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
- [ ] 6.T3 Testes de schema Pydantic: inputs inválidos para MessageCreate, MessageQuery (cursor inválido, contrato inexistente, conteúdo vazio)

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
- [ ] 7.T3 Testes de schema Pydantic: inputs inválidos para ReviewCreate (rating fora de range, texto vazio, contrato não completado, dimensões ausentes)

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
- [ ] 8.T3 Testes de schema Pydantic: inputs inválidos para ProfessionalUpdate, FavoriteCreate (profissional inexistente, campos obrigatórios ausentes, tipos errados)

### 8.I Implementação
- [ ] 8.1 Painel do cliente: pedidos ativos, histórico, bids recebidos, favoritos
- [ ] 8.2 Painel do profissional: agenda, bids pendentes, métricas de earnings e conversão
- [ ] 8.3 Endpoint PATCH /professionals/me para atualização de perfil + re-indexação Typesense
- [ ] 8.4 Endpoint GET /professionals/me/metrics (earnings, conversão, reputation)
- [ ] 8.5 Lista de favoritos: POST /favorites e GET /favorites
- [ ] 8.6 Painel admin: aprovação de profissionais, flags de fraude, KPIs gerais
- [ ] 8.7 Sistema de notificações: in-app via WebSocket + push PWA (Service Worker)

---

## 9. Busca e Descoberta

### 9.T Testes (TDD — escrever antes da implementação)
- [ ] 9.T1 Testes unitários: lógica de filtro geo + full-text, cálculo de clustering de pins, construção de query Typesense, geração de embeddings para pgvector
- [ ] 9.T2 Testes de integração (pytest + httpx): GET /search/professionals com combinações de filtros (q, lat/lng, radius_km, category), worker de indexação — com banco real + Typesense
- [ ] 9.T3 Testes de schema Pydantic: inputs inválidos para SearchQuery (radius negativo, coordenadas fora de range, categoria inexistente, paginação inválida)

### 9.I Implementação
- [ ] 9.1 Configurar Typesense com schema de profissionais (nome, bio, categorias, geo, scores)
- [ ] 9.2 Endpoint GET /search/professionals com filtros: q, lat/lng, radius_km, category
- [ ] 9.3 Worker de indexação automática ao aprovar/atualizar profissional
- [ ] 9.4 Integrar pgvector (embedding de perfil) para busca por similaridade semântica
- [ ] 9.5 Página de busca no frontend com mapa interativo (Leaflet.js ou Google Maps)
- [ ] 9.6 Clustering de pins no mapa para áreas com muitos profissionais

---

## 10. Observabilidade e Go-Live

- [ ] 10.1 OpenTelemetry traces em todos os serviços (BFF, matching, workers)
- [ ] 10.2 Dashboard Grafana: latência de matching, taxa de conversão, MAU, GMV
- [ ] 10.3 Testes de carga no matching engine (k6) — alvo: < 80ms p99
- [ ] 10.4 Checklist de segurança: OWASP Top 10, rate limiting, sanitização de inputs
- [ ] 10.5 Testes E2E do fluxo principal: registro → pedido → match → bid → contrato → pagamento → review
- [ ] 10.6 Deploy em produção: VPS com Docker Compose (Railway, Render ou VPS próprio)
- [ ] 10.7 Configurar HTTPS, domínio e DNS
- [ ] 10.8 Monitoramento: alertas de uptime, CPU/RAM dos containers
