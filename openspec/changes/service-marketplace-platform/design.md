# Design: Service Marketplace Platform

## Contexto

Plataforma marketplace de serviços locais no Brasil, conectando clientes a profissionais verificados (pedreiros, encanadores, advogados, arquitetos, etc.). O diferencial competitivo está em três pilares de IA: análise de imagens do problema (VLM), motor de matching com LTR e reputação granular via NLP em PT-BR.

**Restrições de contexto:**
- Equipe pequena → priorizar managed services e APIs externas sobre infraestrutura própria
- v1 é web responsivo + PWA, sem apps nativos
- Modelo de receita: comissão por transação concluída (sem custo de lead para profissional)

## Goals / Non-Goals

**Goals:**
- Sistema de matching com latência < 80ms para top-10 profissionais
- Pipeline de análise de imagem assíncrono (sem bloquear o fluxo de pedido)
- Schema de banco extensível que comporta toda a v1 sem migrations destrutivas
- Deploy com Docker Compose; path claro para Kubernetes se necessário

**Non-Goals:**
- Modelos de IA treinados from-scratch
- Serviços internacionais ou multi-moeda
- App nativo iOS/Android

---

## Arquitetura Geral

```
                         ┌─────────────────────┐
                         │      Clientes        │
                         │  (Web / PWA Mobile)  │
                         └──────────┬──────────┘
                                    │ HTTPS
                         ┌──────────▼──────────┐
                         │    API Consolidade   │
                         │  (FastAPI + Matching │
                         │     + Storage FS)    │
                         └──────────┬──────────┘
            ┌──────────────────────┼┴─────────────────────┐
            ▼                      ▼                       ▼
   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
   │    PostgreSQL    │  │      Redis       │  │    Filesystem    │
   │  (FTS + PostGIS  │  │ (cache +         │  │    (Uploads)     │
   │   + pgvector)    │  │  pub/sub)        │  │                  │
   └──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## Stack de Tecnologias

| Camada            | Tecnologia                       | Justificativa                                          |
|-------------------|----------------------------------|--------------------------------------------------------|
| **Frontend**      | Next.js 14 (App Router) + TS     | SSR p/ SEO, componentes server, routing built-in      |
| **UI**            | Tailwind CSS + Radix UI          | Design system consistente, acessível                  |
| **Backend (BFF)** | Python + FastAPI (REST)          | Pydantic v2 para validação; runtime Python compartilhado com o matching service; async nativo com asyncpg |
| **Matching ML**   | Python + FastAPI                 | LightGBM nativo em Python; microservice isolado       |
| **Auth**          | JWT + OAuth2 (Google)            | Stateless, refresh token rotation                     |
| **DB Principal**  | PostgreSQL 16 + PostGIS          | Geo-queries nativas, ACID, maturidade                 |
| **Vetorial**      | pgvector (extensão Postgres)     | Embeddings sem infraestrutura adicional               |
| **Cache / Fila**  | Redis (self-hosted)              | Sessions, pub/sub notificações, job queues (arq)      |
| **Busca**         | PostgreSQL FTS + PostGIS         | Full-text PT-BR + geo-search integrado no banco       |
| **Blob Storage**  | Filesystem Local (Dev) / S3      | Fotos do problema, docs; abstração de storage local   |
| **IA - Imagens**  | Google Gemini Vision API         | Zero fine-tuning, custo controlado por token          |
| **IA - NLP**      | BERTimbau (HuggingFace) via API  | Pré-treinado em PT-BR, sentimento + extração          |
| **ML Matching**   | LightGBM (Módulo Python Interno) | LTR integrado ao backend principal para v1             |
| **Pagamento**     | MercadoPago (BR)                 | PIX nativo, suporte split-payment (marketplace)       |
| **Email/SMS**     | Resend (email) + Twilio (SMS)    | Transacionais: confirmações, alertas                  |
| **Deploy**        | Docker + Docker Compose (4 cont) | Topologia enxuta: db, redis, api, web                 |
| **Monitoramento** | Structured Logging (Uvicorn)      | Logs JSON estruturados; OTEL reservado para v2        |

---

## Decisões Técnicas

### D1: FastAPI como BFF em vez de Fastify/Express
- **Escolha**: FastAPI (Python)
- **Alternativas**: Fastify (Node.js), NestJS, Express
- **Razão**: Compartilha runtime Python com o matching service, eliminando um segundo runtime (Node.js) no backend; Pydantic v2 para validação de schema end-to-end; `async def` + `asyncpg` para I/O não-bloqueante; workers assíncronos via ARQ (Python) em vez de BullMQ (Node.js)

### D2: pgvector em vez de Pinecone/Weaviate para embeddings de perfil
- **Escolha**: pgvector como extensão do PostgreSQL
- **Alternativas**: Pinecone, Weaviate, Qdrant
- **Razão**: Evita infra adicional no v1; PostgreSQL já é o banco principal; embeddings de ~1536 dims com IVFFlat são suficientes para milhares de profissionais

### D3: Matching Engine como Módulo Interno
- **Escolha**: Módulo `app.matching` dentro da API FastAPI
- **Alternativas**: Microserviço separado (D3 original), processamento no Worker
- **Razão**: Latência zero de rede; compartilhamento de runtime Python e modelos de dados Pydantic; simplificação operacional da v1. Extensível para microserviço se necessário no futuro.

### D4: PostgreSQL FTS em vez de Typesense
- **Escolha**: PostgreSQL Full-Text Search + PostGIS
- **Alternativas**: Typesense, Elasticsearch
- **Razão**: Remove um container de infraestrutura e a necessidade de sincronizar índices externos; PostgreSQL FTS com dicionário PT-BR é suficiente para a escala da v1.

### D5: Redis pub/sub para WebSocket horizontal
- **Escolha**: `python-socketio` + Redis Adapter (`aioredis`)
- **Razão**: Mesmo padrão do Socket.io mas em Python nativo; permite múltiplas instâncias do BFF sem perder mensagens de chat; Redis já está na infra para filas e workers ARQ; elimina dependência de Node.js no backend

---

## Banco de Dados — Modelo Relacional (PostgreSQL)

### Tabelas Principais

```sql
-- Usuários (base para profissionais e clientes)
users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  email       TEXT UNIQUE NOT NULL,
  phone       TEXT,
  role        TEXT CHECK (role IN ('client','professional','admin')),
  avatar_url  TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
)

-- Profissionais (extensão de users)
professionals (
  id                  UUID PRIMARY KEY REFERENCES users(id),
  bio                 TEXT,
  location            GEOMETRY(Point, 4326),  -- PostGIS
  service_radius_km   FLOAT DEFAULT 20,
  avg_response_min    INT,
  completed_jobs      INT DEFAULT 0,
  reputation_score    FLOAT DEFAULT 0.0,      -- score agregado
  cancel_rate         FLOAT DEFAULT 0.0,
  is_verified         BOOLEAN DEFAULT false,
  hourly_rate_cents   INT,
  profile_embedding   vector(1536)            -- pgvector: embedding do perfil
)

-- Categorias de serviço
categories (
  id        UUID PRIMARY KEY,
  name      TEXT NOT NULL,        -- ex: "Encanamento", "Advocacia"
  slug      TEXT UNIQUE,
  parent_id UUID REFERENCES categories(id)   -- árvore de categorias
)

-- Especialidades do profissional
professional_categories (
  professional_id  UUID REFERENCES professionals(id),
  category_id      UUID REFERENCES categories(id),
  years_experience INT,
  is_primary       BOOLEAN DEFAULT false,
  PRIMARY KEY (professional_id, category_id)
)

-- Pedidos de serviço (do cliente)
requests (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       UUID REFERENCES users(id),
  category_id     UUID REFERENCES categories(id),
  title           TEXT NOT NULL,
  description     TEXT,
  location        GEOMETRY(Point, 4326),
  urgency         TEXT CHECK (urgency IN ('immediate','scheduled','flexible')),
  budget_cents    INT,
  status          TEXT CHECK (status IN ('open','matched','in_progress','done','cancelled')),
  ai_complexity   TEXT,             -- output da VLM: simple/medium/complex
  ai_urgency      TEXT,             -- output da VLM: low/medium/high
  ai_specialties  TEXT[],           -- output da VLM: especialidades detectadas
  created_at      TIMESTAMPTZ DEFAULT now()
)

-- Fotos anexadas ao pedido
request_images (
  id          UUID PRIMARY KEY,
  request_id  UUID REFERENCES requests(id),
  url         TEXT NOT NULL,
  analyzed    BOOLEAN DEFAULT false,
  created_at  TIMESTAMPTZ DEFAULT now()
)

-- Propostas / bids dos profissionais
bids (
  id              UUID PRIMARY KEY,
  request_id      UUID REFERENCES requests(id),
  professional_id UUID REFERENCES professionals(id),
  message         TEXT,
  price_cents     INT NOT NULL,
  estimated_hours INT,
  status          TEXT CHECK (status IN ('pending','accepted','rejected')),
  created_at      TIMESTAMPTZ DEFAULT now()
)

-- Contratações confirmadas
contracts (
  id              UUID PRIMARY KEY,
  request_id      UUID REFERENCES requests(id) UNIQUE,
  professional_id UUID REFERENCES professionals(id),
  client_id       UUID REFERENCES users(id),
  agreed_cents    INT NOT NULL,
  status          TEXT CHECK (status IN ('active','completed','disputed','cancelled')),
  started_at      TIMESTAMPTZ,
  completed_at    TIMESTAMPTZ
)

-- Avaliações
reviews (
  id              UUID PRIMARY KEY,
  contract_id     UUID REFERENCES contracts(id) UNIQUE,
  reviewer_id     UUID REFERENCES users(id),
  reviewee_id     UUID REFERENCES users(id),
  rating          INT CHECK (rating BETWEEN 1 AND 5),
  text            TEXT,
  -- Scores NLP por dimensão (preenchido pelo pipeline de análise)
  score_punctuality   FLOAT,  -- pontualidade
  score_quality       FLOAT,  -- qualidade técnica
  score_cleanliness   FLOAT,  -- limpeza/acabamento
  score_communication FLOAT,  -- comunicação
  is_authentic        BOOLEAN DEFAULT true,  -- flag anti-fake
  created_at          TIMESTAMPTZ DEFAULT now()
)

-- Mensagens do chat in-app
messages (
  id          UUID PRIMARY KEY,
  contract_id UUID REFERENCES contracts(id),
  sender_id   UUID REFERENCES users(id),
  content     TEXT,
  created_at  TIMESTAMPTZ DEFAULT now()
)

-- Notificações
notifications (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES users(id),
  type        TEXT NOT NULL,  -- 'bid_received', 'bid_accepted', 'message', 'review_request'
  payload     JSONB,
  read_at     TIMESTAMPTZ,
  created_at  TIMESTAMPTZ DEFAULT now()
)
```

### Índices Críticos para Performance

```sql
-- Geo-search de profissionais próximos ao pedido
CREATE INDEX idx_professionals_location ON professionals USING GIST(location);

-- Busca de pedidos abertos por categoria
CREATE INDEX idx_requests_status_category ON requests(status, category_id);

-- Matching vector similarity (pgvector)
CREATE INDEX idx_professionals_embedding ON professionals USING ivfflat (profile_embedding vector_cosine_ops);

-- Notificações não lidas por usuário
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, read_at) WHERE read_at IS NULL;
```

---

## Pipeline da Análise de Imagem (VLM)

```
  upload de foto → S3/MinIO
         │
         ▼
  Worker (BullMQ / Redis Queue)
         │
         ▼
  Gemini Vision API
  Prompt: "Analise o problema na imagem. Retorne JSON:
  { complexity, urgency, specialties[], materials[] }"
         │
         ▼
  UPDATE requests SET ai_complexity=..., ai_urgency=..., ai_specialties=...
         │
         ▼
  Matching Engine re-rankeia candidatos com as novas features
```

**Fallback**: se Gemini Vision retornar erro ou timeout > 10s, `ai_*` ficam `null` e o matching usa apenas features tradicionais. O worker retenta até 3× com backoff exponencial.

---

## Motor de Matching — LTR (Learning to Rank)

### Features do Modelo LightGBM

```python
features = {
    # Geo
    "distance_km": float,
    "within_service_radius": bool,

    # Reputação
    "reputation_score": float,       # score agregado
    "score_punctuality": float,      # NLP de reviews
    "score_quality": float,
    "cancel_rate": float,
    "completed_jobs": int,

    # Competência
    "category_match_score": float,   # 1.0 se primária, 0.5 se secundária
    "years_experience": int,
    "is_verified": bool,

    # Preço
    "price_vs_budget_ratio": float,  # bid_price / client_budget

    # Disponibilidade
    "avg_response_time_min": int,
    "urgency_match": bool,           # profissional disponível p/ urgência?

    # IA do pedido
    "ai_complexity_match": float,    # complexidade vs. senioridade do prof.
    "specialty_overlap": float,      # overlap entre ai_specialties e categorias do prof.
}
```

### Treinamento e Feedback Loop

```
  Label positiva: cliente contratou o profissional
  Label negativa: profissional foram mostrados mas ignorados

  Treino: GBDT com objective="lambdarank"
  Re-treino: semanal com novos dados de contratação

  Serving: microservice Python (FastAPI) chamado pelo BFF
  Latência alvo: < 80ms p/ retornar top-10 profissionais
```

**Matching v0 (cold-start)**: enquanto não há dados suficientes para LTR, usar matching baseado em regras: geo-radius < 20km + match de categoria + reputation_score desc.

---

## Pipeline NLP de Reviews

```
  Review de texto salva no banco
         │
         ▼
  Worker analisa com BERTimbau (ou Gemini via API como fallback)
         │
         ▼
  Extrai scores por dimensão:
  {
    punctuality: 0.92,
    quality:     0.88,
    cleanliness: 0.45,
    communication: 0.70
  }
         │
         ├──▶ Detecta autenticidade (threshold de suspeita)
         │
         ▼
  UPDATE reviews SET score_*..., is_authentic=...
         │
         ▼
  Recalcula reputation_score do professional:
  score = 0.3*avg(quality) + 0.25*avg(punctuality)
        + 0.2*avg(communication) + 0.15*avg(cleanliness)
        + 0.1*(completed_jobs_factor)
```

---

## Anti-Desintermediação

Para proteger a comissão quando cliente e profissional tentam "fechar por fora":

1. **Chat monitorado** — NLP detecta padrões como "meu WhatsApp é...", "me chame no..." → alerta automático para admin.
2. **Pagamento obrigatório in-app** — serviço só marcado como concluído se pago via plataforma; sem pagamento = sem review e sem badge.
3. **Incentivos positivos** — profissionais com histórico in-app ganham badge "Verificado Platinum" e sobem no ranking.

---

## Riscos / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Custo Gemini Vision em escala | Rate limiting + cache de resultados por hash de imagem; fallback para análise sem VLM |
| Cold-start do modelo LTR sem dados | Matching v0 por regras até ter 500+ contratos históricos |
| Latência BERTimbau via API | Análise de NLP é assíncrona, não bloqueia fluxo de review |
| Desintermediação persistente | Combinação de monitoramento + incentivos financeiros |
| Split-payment MercadoPago complexo | Testar marketplace mode em sandbox antes de go-live |

---

## Plano de Migração / Deploy

1. **Fase 1**: `docker-compose up` com PostgreSQL + Redis + MinIO local
2. **Fase 2**: Migrations iniciais + seed de categorias
3. **Fase 3**: BFF Fastify + Next.js com auth funcional
4. **Fase 4**: Pipeline VLM + matching v0 (regras)
5. **Fase 5**: Pagamentos sandbox → produção
6. **Fase 6**: Coleta de dados de treinamento → modelo LTR v1
7. **Go-live**: Deploy em VPS (Railway, Render ou VPS próprio) com Docker Compose

**Rollback**: cada fase tem migrations reversíveis; serviços são stateless (BFF, matching), apenas o PostgreSQL retém estado crítico.

---

## Questões em Aberto

- [ ] Qual % de comissão por transação? (impacta split-payment no MercadoPago)
- [ ] Categorias iniciais: ~20 definidas, validar com pesquisa de mercado
- [ ] BERTimbau via HuggingFace Inference API ou self-hosted? (custo vs. latência)
- [ ] Geolocalização: permitir profissional editar raio de atendimento no perfil?
- [ ] Disputa de contratos: fluxo de mediação humana ou automatizado?
