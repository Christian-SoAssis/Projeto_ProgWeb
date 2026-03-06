# Design: Service Marketplace Platform

## Arquitetura Geral

```
                         ┌─────────────────────┐
                         │      Clientes        │
                         │  (Web / PWA Mobile)  │
                         └──────────┬──────────┘
                                    │ HTTPS
                         ┌──────────▼──────────┐
                         │    API Gateway /     │
                         │  BFF (Backend For    │
                         │     Frontend)        │
                         └──────────┬──────────┘
            ┌──────────────────────┬┴─────────────────────┐
            ▼                      ▼                       ▼
  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
  │  Auth Service    │  │ Matching Service │  │  Media/AI Service│
  │  (JWT + OAuth2)  │  │  (LTR Engine)    │  │  (VLM + NLP)     │
  └──────────────────┘  └──────────────────┘  └──────────────────┘
            │                      │                       │
            └──────────────────────┴───────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌─────────────┐ ┌──────────┐  ┌──────────────┐
            │ PostgreSQL  │ │  Redis   │  │   S3/MinIO   │
            │ + PostGIS   │ │ (cache + │  │  (fotos,     │
            │ + pgvector  │ │  pub/sub)│  │   docs)      │
            └─────────────┘ └──────────┘  └──────────────┘
```

---

## Stack de Tecnologias

| Camada            | Tecnologia                       | Justificativa                                          |
|-------------------|----------------------------------|--------------------------------------------------------|
| **Frontend**      | Next.js 14 (App Router) + TS     | SSR p/ SEO, componentes server, routing built-in      |
| **UI**            | Tailwind CSS + Radix UI          | Design system consistente, acessível                  |
| **Backend**       | Node.js + Fastify (API REST)     | Baixa latência, schema validation nativa (json-schema)|
| **Auth**          | JWT + OAuth2 (Google/GitHub)     | Stateless, refresh token rotation                     |
| **DB Principal**  | PostgreSQL 16 + PostGIS          | Geo-queries nativas, ACID, maturidade                 |
| **Vetorial**      | pgvector (extensão Postgres)     | Embeddings de reviews/profissionais sem infra extra   |
| **Cache / Fila**  | Redis (Upstash ou self-hosted)   | Sessions, pub/sub notificações, job queues            |
| **Busca**         | Elasticsearch ou Typesense       | Full-text PT-BR + geo-search de profissionais         |
| **Blob Storage**  | MinIO (self-hosted) ou S3        | Fotos do problema, documentos de certificação         |
| **IA - Imagens**  | Google Gemini Vision API         | Zero fine-tuning, custo controlado por token          |
| **IA - NLP**      | BERTimbau (HuggingFace) via API  | Pré-treinado em PT-BR, sentimento + extração          |
| **ML Matching**   | LightGBM (Python microservice)   | LTR com features tabulares, explainability            |
| **Pagamento**     | MercadoPago (BR) / Stripe        | PIX nativo, suporte split-payment (marketplace)       |
| **Email/SMS**     | Resend (email) + Twilio (SMS)    | Transacionais: confirmações, alertas                  |
| **Deploy**        | Docker + Docker Compose (v1)     | Portável; evolui para Kubernetes se necessário        |
| **Monitoramento** | OpenTelemetry + Grafana          | Traces, logs, métricas de latência de matching        |

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
```

### Índices Críticos para Performance

```sql
-- Geo-search de profissionais próximos ao pedido
CREATE INDEX idx_professionals_location ON professionals USING GIST(location);

-- Busca de pedidos abertos por categoria
CREATE INDEX idx_requests_status_category ON requests(status, category_id);

-- Matching vector similarity (pgvector)
CREATE INDEX idx_professionals_embedding ON professionals USING ivfflat (profile_embedding vector_cosine_ops);
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

---

## Pipeline NLP de Reviews

```
  Review de texto salva no banco
         │
         ▼
  Worker analisa com BERTimbau (ou Gemini via API)
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

1. **Chat monitorado** — NLP detecta padrões como "meu WhatsApp é...", "me chame no..." → alerta automático.
2. **Pagamento obrigatório in-app** — serviço só marcado como concluído se pago via plataforma; sem pagamento = sem review.
3. **Incentivos positivos** — profissionais com histórico in-app ganham badge "Verificado Platinum" e sobem no ranking.
