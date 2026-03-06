# Tasks: Service Marketplace Platform

## Fase 1 — Fundação e Infra

- [ ] Configurar monorepo (Next.js frontend + Fastify backend)
- [ ] Configurar Docker Compose (PostgreSQL + PostGIS + Redis + MinIO)
- [ ] Instalar extensões PostgreSQL: `PostGIS`, `pgvector`, `uuid-ossp`
- [ ] Executar migrations do schema principal (tabelas do design.md)
- [ ] Configurar variáveis de ambiente (`.env.example`)
- [ ] Pipeline CI básica (lint + type-check + testes)

---

## Fase 2 — Auth e Cadastro

- [ ] Implementar JWT (access token + refresh token rotation)
- [ ] OAuth2 social login (Google)
- [ ] Endpoint de cadastro de cliente
- [ ] Endpoint de cadastro de profissional (com upload de documentos para S3)
- [ ] Fluxo de verificação de profissional (admin aprova)

---

## Fase 3 — Pedido de Serviço + Análise de Imagem

- [ ] CRUD de categorias (seed inicial: ~20 categorias)
- [ ] Criar endpoint `POST /requests` com upload de imagens
- [ ] Configurar worker BullMQ para processar imagens assíncronamente
- [ ] Integrar Gemini Vision API no worker de análise
- [ ] Salvar output da VLM nos campos `ai_*` da tabela `requests`
- [ ] Endpoint de listagem de pedidos para o cliente

---

## Fase 4 — Motor de Matching

- [ ] Endpoint `GET /requests/:id/matches` que retorna profissionais rankeados
- [ ] Implementar matching v0 baseado em regras (geo + categoria + reputação)
- [ ] Microservice Python (FastAPI) com modelo LightGBM LTR
- [ ] Coletar dados de treinamento (log de impressões vs. contratações)
- [ ] Treinar primeiro modelo e substituir matching baseado em regras
- [ ] Configurar re-treino semanal automatizado

---

## Fase 5 — Bids, Contratos e Pagamento

- [ ] Endpoint `POST /bids` (profissional envia orçamento)
- [ ] Endpoint `PATCH /bids/:id` (cliente aceita/rejeita)
- [ ] Criação automática de `contracts` ao aceitar bid
- [ ] Integração com MercadoPago (split-payment marketplace)
- [ ] Webhook de confirmação de pagamento → atualiza status do contrato

---

## Fase 6 — Chat In-App

- [ ] WebSocket com Socket.io (via Redis pub/sub para horizontalidade)
- [ ] Persistência de mensagens na tabela `messages`
- [ ] Worker de NLP para detectar tentativas de desintermediação
- [ ] Alerta para admin quando padrão suspeito detectado

---

## Fase 7 — Reviews e Reputação Granular

- [ ] Endpoint `POST /reviews` (após contrato concluído)
- [ ] Worker NLP com BERTimbau → scores por dimensão
- [ ] Detecção de reviews inautênticas (flag `is_authentic`)
- [ ] Recálculo do `reputation_score` do profissional
- [ ] Componente "radar" de reputação no perfil do profissional

---

## Fase 8 — Painéis e UX

- [ ] Painel do cliente: pedidos ativos, histórico, profissionais favoritos
- [ ] Painel do profissional: agenda, bids pendentes, métricas, earnings
- [ ] Painel admin: aprovação de profissionais, monitoring, flags de fraude
- [ ] Notificações push (PWA) via Redis pub/sub

---

## Fase 9 — Busca e Descoberta

- [ ] Integrar Typesense (ou Elasticsearch) com dados de profissionais
- [ ] Indexar profissionais com embedding de perfil (pgvector)
- [ ] Endpoint de busca geo + full-text + filtros de categoria/preço
- [ ] Página de busca no frontend com mapa interativo

---

## Fase 10 — Observabilidade e Go-Live

- [ ] OpenTelemetry traces em todos os serviços
- [ ] Dashboard Grafana: latência de matching, taxa de conversão, MAU
- [ ] Testes de carga no matching engine (k6)
- [ ] Checklist de segurança (OWASP Top 10)
- [ ] Deploy em produção (VPS com Docker Compose ou Railway/Render)
