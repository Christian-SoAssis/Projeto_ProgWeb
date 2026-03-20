# Spec: database

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Diagrama ERD

```mermaid
erDiagram
    users ||--o| professionals : "extends"
    users ||--o{ consent_logs : "has"
    users ||--o{ push_subscriptions : "has"
    users ||--o{ requests : "creates"
    users ||--o{ notifications : "receives"
    users ||--o{ reviews : "writes (reviewer)"
    users ||--o{ reviews : "receives (reviewee)"
    users ||--o{ messages : "sends"
    users ||--o{ contracts : "client"
    users ||--o{ favorites : "has"

    professionals ||--o{ professional_categories : "has"
    professionals ||--o{ bids : "sends"
    professionals ||--o{ contracts : "professional"

    categories ||--o{ categories : "parent"
    categories ||--o{ professional_categories : "has"
    categories ||--o{ requests : "belongs"
    categories ||--o{ commission_rates : "has"

    requests ||--o{ request_images : "has"
    requests ||--o{ bids : "receives"
    requests ||--o| contracts : "generates"

    contracts ||--o{ messages : "has"
    contracts ||--o| reviews : "has"
    contracts ||--o| disputes : "has"

    users {
        UUID id PK
        TEXT name
        TEXT email
        TEXT phone
        TEXT password_hash
        TEXT role
        TEXT avatar_url
        BOOLEAN is_active
        TIMESTAMPTZ last_login_at
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    professionals {
        UUID id PK_FK
        TEXT bio
        GEOMETRY location
        FLOAT service_radius_km
        INT avg_response_min
        INT completed_jobs
        FLOAT reputation_score
        FLOAT cancel_rate
        BOOLEAN is_verified
        INT hourly_rate_cents
        VECTOR profile_embedding
        TIMESTAMPTZ verified_at
    }

    categories {
        UUID id PK
        TEXT name
        TEXT slug
        UUID parent_id FK
        INT sort_order
        BOOLEAN is_active
    }

    professional_categories {
        UUID professional_id PK_FK
        UUID category_id PK_FK
        INT years_experience
        BOOLEAN is_primary
    }

    requests {
        UUID id PK
        UUID client_id FK
        UUID category_id FK
        TEXT title
        TEXT description
        GEOMETRY location
        TEXT urgency
        INT budget_cents
        TEXT status
        TEXT ai_complexity
        TEXT ai_urgency
        TEXT_ARRAY ai_specialties
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    request_images {
        UUID id PK
        UUID request_id FK
        TEXT url
        TEXT content_type
        INT size_bytes
        BOOLEAN analyzed
        TIMESTAMPTZ created_at
    }

    bids {
        UUID id PK
        UUID request_id FK
        UUID professional_id FK
        TEXT message
        INT price_cents
        INT estimated_hours
        TEXT status
        TIMESTAMPTZ created_at
    }

    contracts {
        UUID id PK
        UUID request_id FK
        UUID professional_id FK
        UUID client_id FK
        INT agreed_cents
        TEXT status
        TIMESTAMPTZ started_at
        TIMESTAMPTZ payment_confirmed_at
        TIMESTAMPTZ payout_scheduled_at
        TIMESTAMPTZ payout_completed_at
        TIMESTAMPTZ completed_at
    }

    reviews {
        UUID id PK
        UUID contract_id FK
        UUID reviewer_id FK
        UUID reviewee_id FK
        INT rating
        TEXT text
        FLOAT score_punctuality
        FLOAT score_quality
        FLOAT score_cleanliness
        FLOAT score_communication
        BOOLEAN is_authentic
        TIMESTAMPTZ created_at
    }

    messages {
        UUID id PK
        UUID contract_id FK
        UUID sender_id FK
        TEXT content
        TIMESTAMPTZ created_at
    }

    notifications {
        UUID id PK
        UUID user_id FK
        TEXT type
        JSONB payload
        TIMESTAMPTZ read_at
        TIMESTAMPTZ created_at
    }

    disputes {
        UUID id PK
        UUID contract_id FK
        UUID opened_by_user_id FK
        TEXT reason
        TEXT category
        TEXT_ARRAY evidence_urls
        TEXT status
        TEXT resolution
        INT refund_percent
        TEXT admin_notes
        TEXT response_message
        TEXT_ARRAY response_evidence_urls
        TEXT proposed_resolution
        TIMESTAMPTZ response_deadline
        TIMESTAMPTZ responded_at
        TIMESTAMPTZ resolved_at
        TIMESTAMPTZ created_at
    }

    commission_rates {
        UUID id PK
        UUID category_id FK
        NUMERIC percent
        DATE effective_from
        DATE effective_until
    }

    consent_logs {
        UUID id PK
        UUID user_id FK
        TEXT consent_type
        TEXT version
        TEXT ip_address
        TEXT user_agent
        TIMESTAMPTZ accepted_at
    }

    push_subscriptions {
        UUID id PK
        UUID user_id FK
        TEXT endpoint
        TEXT key_p256dh
        TEXT key_auth
        TEXT device_label
        BOOLEAN is_active
        TIMESTAMPTZ created_at
        TIMESTAMPTZ last_used_at
    }

    favorites {
        UUID id PK
        UUID client_id FK
        UUID professional_id FK
        TIMESTAMPTZ created_at
    }
```

---

## Requirement: Extensões PostgreSQL

O banco **MUST** ter as seguintes extensões instaladas antes de qualquer migration:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "vector";    -- pgvector
```

---

## Requirement: Tabela `users`

Tabela base para todos os tipos de usuário (cliente, profissional, admin).

```sql
CREATE TABLE users (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT        NOT NULL,
    email           TEXT        NOT NULL,
    phone           TEXT,
    password_hash   TEXT,                           -- NULL se cadastro via OAuth2
    role            TEXT        NOT NULL CHECK (role IN ('client', 'professional', 'admin')),
    avatar_url      TEXT,
    is_active       BOOLEAN     NOT NULL DEFAULT true,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE INDEX idx_users_role ON users (role);
CREATE INDEX idx_users_email_lower ON users (lower(email));
```

### Constraints
- `email` **MUST** ser UNIQUE (case-insensitive via índice)
- `password_hash` **MAY** ser NULL para contas OAuth2
- `role` **MUST** ser um dos valores do CHECK
- `is_active` **MUST** default `true`; `false` para contas anonimizadas (LGPD)

---

## Requirement: Tabela `professionals`

Extensão de `users` para profissionais com dados de localização, reputação e embedding vetorial.

```sql
CREATE TABLE professionals (
    id                  UUID        PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    bio                 TEXT,
    location            GEOMETRY(Point, 4326),          -- PostGIS (longitude, latitude)
    service_radius_km   FLOAT       NOT NULL DEFAULT 20.0,
    avg_response_min    INT,
    completed_jobs      INT         NOT NULL DEFAULT 0,
    reputation_score    FLOAT       NOT NULL DEFAULT 0.0 CHECK (reputation_score >= 0 AND reputation_score <= 5),
    cancel_rate         FLOAT       NOT NULL DEFAULT 0.0 CHECK (cancel_rate >= 0 AND cancel_rate <= 1),
    is_verified         BOOLEAN     NOT NULL DEFAULT false,
    hourly_rate_cents   INT         CHECK (hourly_rate_cents > 0),
    profile_embedding   vector(1536),                    -- pgvector
    verified_at         TIMESTAMPTZ
);

-- Geo-search: profissionais próximos ao pedido
CREATE INDEX idx_professionals_location ON professionals USING GIST (location);

-- Busca por similaridade vetorial (perfil)
CREATE INDEX idx_professionals_embedding ON professionals USING ivfflat (profile_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Filtro: apenas verificados
CREATE INDEX idx_professionals_verified ON professionals (is_verified) WHERE is_verified = true;

-- Ranking por reputação
CREATE INDEX idx_professionals_reputation ON professionals (reputation_score DESC);
```

### Constraints
- FK para `users.id` com **ON DELETE CASCADE** (exclusão de conta remove perfil)
- `reputation_score` **MUST** estar entre 0 e 5
- `cancel_rate` **MUST** estar entre 0 e 1
- `hourly_rate_cents` **MUST** ser positivo se presente
- `service_radius_km` **MUST** default 20 km

---

## Requirement: Tabela `categories`

Árvore hierárquica de categorias de serviço (auto-referência via `parent_id`).

```sql
CREATE TABLE categories (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT    NOT NULL,
    slug        TEXT    NOT NULL,
    parent_id   UUID    REFERENCES categories(id) ON DELETE SET NULL,
    sort_order  INT     NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT uq_categories_slug UNIQUE (slug)
);

CREATE INDEX idx_categories_parent ON categories (parent_id);
CREATE INDEX idx_categories_active ON categories (is_active) WHERE is_active = true;
```

---

## Requirement: Tabela `professional_categories`

Relacionamento N:N entre profissionais e categorias.

```sql
CREATE TABLE professional_categories (
    professional_id UUID NOT NULL REFERENCES professionals(id) ON DELETE CASCADE,
    category_id     UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    years_experience INT CHECK (years_experience >= 0),
    is_primary      BOOLEAN NOT NULL DEFAULT false,

    PRIMARY KEY (professional_id, category_id)
);

CREATE INDEX idx_profcat_category ON professional_categories (category_id);
```

---

## Requirement: Tabela `requests`

Pedidos de serviço criados por clientes.

```sql
CREATE TABLE requests (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id       UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id     UUID        NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    title           TEXT        NOT NULL CHECK (length(title) >= 5),
    description     TEXT,
    location        GEOMETRY(Point, 4326) NOT NULL,
    urgency         TEXT        NOT NULL CHECK (urgency IN ('immediate', 'scheduled', 'flexible')),
    budget_cents    INT         CHECK (budget_cents > 0),
    status          TEXT        NOT NULL DEFAULT 'open'
                                CHECK (status IN ('open', 'matched', 'in_progress', 'done', 'cancelled')),
    ai_complexity   TEXT        CHECK (ai_complexity IN ('simple', 'medium', 'complex')),
    ai_urgency      TEXT        CHECK (ai_urgency IN ('low', 'medium', 'high')),
    ai_specialties  TEXT[],
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Pedidos abertos por categoria (matching)
CREATE INDEX idx_requests_status_category ON requests (status, category_id);

-- Pedidos de um cliente
CREATE INDEX idx_requests_client ON requests (client_id, created_at DESC);

-- Geo-search de pedidos
CREATE INDEX idx_requests_location ON requests USING GIST (location);
```

### Constraints
- `title` **MUST** ter no mínimo 5 caracteres
- `category_id` com **ON DELETE RESTRICT** (não excluir categoria com pedidos)
- `client_id` com **ON DELETE CASCADE** (anonimização LGPD)
- `status` **MUST** default `'open'`

---

## Requirement: Tabela `request_images`

Imagens anexas a um pedido (máximo 5, até 10MB cada — validado na API).

```sql
CREATE TABLE request_images (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id  UUID        NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    url         TEXT        NOT NULL,
    content_type TEXT       NOT NULL CHECK (content_type IN ('image/jpeg', 'image/png', 'image/webp')),
    size_bytes  INT         NOT NULL CHECK (size_bytes > 0 AND size_bytes <= 10485760),  -- max 10MB
    analyzed    BOOLEAN     NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reqimg_request ON request_images (request_id);
CREATE INDEX idx_reqimg_unanalyzed ON request_images (analyzed) WHERE analyzed = false;
```

---

## Requirement: Tabela `bids`

Propostas de profissionais verificados para pedidos abertos.

```sql
CREATE TABLE bids (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id      UUID        NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    professional_id UUID        NOT NULL REFERENCES professionals(id) ON DELETE CASCADE,
    message         TEXT,
    price_cents     INT         NOT NULL CHECK (price_cents > 0),
    estimated_hours INT         CHECK (estimated_hours > 0),
    status          TEXT        NOT NULL DEFAULT 'pending'
                                CHECK (status IN ('pending', 'accepted', 'rejected', 'cancelled')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Um profissional só pode enviar 1 bid por pedido
    CONSTRAINT uq_bids_request_professional UNIQUE (request_id, professional_id)
);

CREATE INDEX idx_bids_request ON bids (request_id, status);
CREATE INDEX idx_bids_professional ON bids (professional_id, created_at DESC);
```

---

## Requirement: Tabela `contracts`

Contratações confirmadas (criadas automaticamente ao aceitar bid).

```sql
CREATE TABLE contracts (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id              UUID        NOT NULL REFERENCES requests(id) ON DELETE RESTRICT,
    professional_id         UUID        NOT NULL REFERENCES professionals(id) ON DELETE RESTRICT,
    client_id               UUID        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    agreed_cents            INT         NOT NULL CHECK (agreed_cents > 0),
    status                  TEXT        NOT NULL DEFAULT 'active'
                                        CHECK (status IN ('active', 'payment_confirmed', 'completed',
                                                          'disputed', 'refunded', 'partially_refunded', 'cancelled')),
    started_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    payment_confirmed_at    TIMESTAMPTZ,
    payout_scheduled_at     TIMESTAMPTZ,
    payout_completed_at     TIMESTAMPTZ,
    completed_at            TIMESTAMPTZ,

    -- Um pedido gera no máximo 1 contrato ativo
    CONSTRAINT uq_contracts_request UNIQUE (request_id)
);

CREATE INDEX idx_contracts_professional ON contracts (professional_id, status);
CREATE INDEX idx_contracts_client ON contracts (client_id, status);
CREATE INDEX idx_contracts_payout ON contracts (status, payout_scheduled_at)
    WHERE status = 'payment_confirmed';
```

### Constraints
- FK com **ON DELETE RESTRICT** — contratos não podem ter partes excluídas diretamente (anonimizar via LGPD flow)
- `request_id` UNIQUE — 1 contrato por pedido

---

## Requirement: Tabela `reviews`

Avaliações com scores NLP por dimensão.

```sql
CREATE TABLE reviews (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id         UUID        NOT NULL REFERENCES contracts(id) ON DELETE RESTRICT,
    reviewer_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reviewee_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating              INT         NOT NULL CHECK (rating BETWEEN 1 AND 5),
    text                TEXT        NOT NULL CHECK (length(text) >= 10),
    score_punctuality   FLOAT       CHECK (score_punctuality >= 0 AND score_punctuality <= 1),
    score_quality       FLOAT       CHECK (score_quality >= 0 AND score_quality <= 1),
    score_cleanliness   FLOAT       CHECK (score_cleanliness >= 0 AND score_cleanliness <= 1),
    score_communication FLOAT       CHECK (score_communication >= 0 AND score_communication <= 1),
    is_authentic        BOOLEAN     NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- 1 review por contrato
    CONSTRAINT uq_reviews_contract UNIQUE (contract_id)
);

CREATE INDEX idx_reviews_reviewee ON reviews (reviewee_id, is_authentic) WHERE is_authentic = true;
CREATE INDEX idx_reviews_reviewer ON reviews (reviewer_id, created_at DESC);
```

---

## Requirement: Tabela `messages`

Mensagens do chat in-app vinculadas a contratos.

```sql
CREATE TABLE messages (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID        NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    sender_id   UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content     TEXT        NOT NULL CHECK (length(content) >= 1),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Histórico paginado por cursor (created_at)
CREATE INDEX idx_messages_contract_cursor ON messages (contract_id, created_at DESC);
```

---

## Requirement: Tabela `notifications`

Notificações in-app com payload JSONB.

```sql
CREATE TABLE notifications (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type        TEXT        NOT NULL CHECK (type IN (
                                'bid_received', 'bid_accepted', 'bid_rejected',
                                'payment_confirmed', 'payout_completed',
                                'new_message', 'review_request',
                                'dispute_opened', 'dispute_response', 'dispute_resolved',
                                'professional_verified', 'professional_rejected',
                                'account_warning'
                            )),
    payload     JSONB       NOT NULL DEFAULT '{}',
    read_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Notificações não lidas por usuário
CREATE INDEX idx_notifications_user_unread ON notifications (user_id, created_at DESC)
    WHERE read_at IS NULL;
```

---

## Requirement: Tabela `disputes`

Disputas de contratos com fluxo completo de arbitragem.

```sql
CREATE TABLE disputes (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id             UUID        NOT NULL REFERENCES contracts(id) ON DELETE RESTRICT,
    opened_by_user_id       UUID        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    reason                  TEXT        NOT NULL CHECK (length(reason) >= 10),
    category                TEXT        NOT NULL CHECK (category IN ('quality', 'no_show', 'overcharge', 'damage', 'other')),
    evidence_urls           TEXT[]      NOT NULL DEFAULT '{}',
    status                  TEXT        NOT NULL DEFAULT 'opened'
                                        CHECK (status IN ('opened', 'under_review', 'auto_escalated', 'resolved')),
    resolution              TEXT        CHECK (resolution IN ('refund_full', 'refund_partial', 'refund_denied')),
    refund_percent          INT         CHECK (refund_percent >= 1 AND refund_percent <= 99),
    admin_notes             TEXT,
    response_message        TEXT,
    response_evidence_urls  TEXT[]      DEFAULT '{}',
    proposed_resolution     TEXT,
    response_deadline       TIMESTAMPTZ NOT NULL,
    responded_at            TIMESTAMPTZ,
    resolved_at             TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- 1 disputa ativa por contrato
    CONSTRAINT uq_disputes_contract UNIQUE (contract_id)
);

CREATE INDEX idx_disputes_status ON disputes (status) WHERE status != 'resolved';
CREATE INDEX idx_disputes_deadline ON disputes (response_deadline) WHERE status = 'opened';
```

---

## Requirement: Tabela `commission_rates`

Taxas de comissão configuráveis por categoria (taxa padrão quando `category_id IS NULL`).

```sql
CREATE TABLE commission_rates (
    id              UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id     UUID    REFERENCES categories(id) ON DELETE CASCADE,
    percent         NUMERIC(5,2) NOT NULL CHECK (percent > 0 AND percent < 100),
    effective_from  DATE    NOT NULL DEFAULT CURRENT_DATE,
    effective_until DATE,

    CHECK (effective_until IS NULL OR effective_until > effective_from)
);

-- Busca da taxa ativa por categoria
CREATE INDEX idx_commission_category_date ON commission_rates (category_id, effective_from DESC);

-- Seed: taxa padrão de 5%
-- INSERT INTO commission_rates (category_id, percent) VALUES (NULL, 5.00);
```

---

## Requirement: Tabela `consent_logs`

Registros de consentimento LGPD (Art. 8 — auditável, imutável).

```sql
CREATE TABLE consent_logs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,  -- RESTRICT: log deve sobreviver
    consent_type    TEXT        NOT NULL CHECK (consent_type IN ('terms', 'privacy', 'marketing')),
    version         TEXT        NOT NULL,       -- versão dos termos aceitos (ex: "2026-01")
    ip_address      INET        NOT NULL,
    user_agent      TEXT        NOT NULL,
    accepted_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Consulta de consentimentos por usuário
CREATE INDEX idx_consent_user ON consent_logs (user_id, consent_type, accepted_at DESC);
```

### Constraints
- FK com **ON DELETE RESTRICT** — logs de consentimento **MUST NOT** ser excluídos (retenção 5 anos LGPD)
- `ip_address` tipo **INET** do PostgreSQL para validação nativa

---

## Requirement: Tabela `push_subscriptions`

Web Push API subscriptions por dispositivo.

```sql
CREATE TABLE push_subscriptions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint        TEXT        NOT NULL,
    key_p256dh      TEXT        NOT NULL,
    key_auth        TEXT        NOT NULL,
    device_label    TEXT,
    is_active       BOOLEAN     NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_used_at    TIMESTAMPTZ,

    -- Um endpoint é único
    CONSTRAINT uq_push_endpoint UNIQUE (endpoint)
);

CREATE INDEX idx_push_user_active ON push_subscriptions (user_id) WHERE is_active = true;
```

---

## Requirement: Tabela `favorites`

Lista de favoritos do cliente (profissionais salvos).

```sql
CREATE TABLE favorites (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id       UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    professional_id UUID        NOT NULL REFERENCES professionals(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_favorites_client_professional UNIQUE (client_id, professional_id)
);

CREATE INDEX idx_favorites_client ON favorites (client_id, created_at DESC);
```

---

## Resumo de Índices

| Tabela | Índice | Tipo | Justificativa |
|--------|--------|------|---------------|
| `professionals` | `idx_professionals_location` | **GiST** | Geo-search PostGIS |
| `professionals` | `idx_professionals_embedding` | **IVFFlat** | Busca vetorial pgvector |
| `professionals` | `idx_professionals_verified` | B-tree parcial | Filtro de verificados |
| `professionals` | `idx_professionals_reputation` | B-tree | Ranking |
| `requests` | `idx_requests_status_category` | B-tree composto | Matching |
| `requests` | `idx_requests_location` | **GiST** | Geo-search |
| `request_images` | `idx_reqimg_unanalyzed` | B-tree parcial | Worker VLM |
| `bids` | `idx_bids_request` | B-tree composto | Listagem de bids por status |
| `contracts` | `idx_contracts_payout` | B-tree parcial | Job de repasse D+2 |
| `messages` | `idx_messages_contract_cursor` | B-tree composto | Paginação cursor-based |
| `notifications` | `idx_notifications_user_unread` | B-tree parcial | Badge de não-lidas |
| `disputes` | `idx_disputes_deadline` | B-tree parcial | Job de expiração 72h |
| `consent_logs` | `idx_consent_user` | B-tree composto | Consulta LGPD |

---

## Ordem de Dependência (Migrations)

```
1. extensions (uuid-ossp, postgis, vector)
2. users              (sem dependência)
3. professionals      (depende: users)
4. categories         (auto-referência)
5. professional_categories (depende: professionals, categories)
6. requests           (depende: users, categories)
7. request_images     (depende: requests)
8. bids               (depende: requests, professionals)
9. contracts          (depende: requests, professionals, users)
10. reviews           (depende: contracts, users)
11. messages          (depende: contracts, users)
12. notifications     (depende: users)
13. disputes          (depende: contracts, users)
14. commission_rates  (depende: categories)
15. consent_logs      (depende: users)
16. push_subscriptions (depende: users)
17. favorites         (depende: users, professionals)
```
