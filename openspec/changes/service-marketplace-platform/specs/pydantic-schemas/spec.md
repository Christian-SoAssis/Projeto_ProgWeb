# Spec: pydantic-schemas

> Schemas Pydantic v2 para todas as tabelas do banco. Cada tabela possui: **Base** (campos compartilhados), **Create** (input POST), **Update** (PATCH parcial, campos Optional), **Response** (output com computed fields). Mapeamento explícito DB ↔ Schema.

---

## 1. Users (Módulo: Auth)

### DB → Schema mapping

| Coluna DB | Tipo DB | Campo Schema | Tipo Pydantic | Notas |
|-----------|---------|-------------|--------------|-------|
| `id` | UUID | `id` | `uuid.UUID` | Response only |
| `name` | TEXT NOT NULL | `name` | `str` | min_length=2, max_length=100 |
| `email` | TEXT UNIQUE NOT NULL | `email` | `EmailStr` | Normalizado para lowercase |
| `phone` | TEXT | `phone` | `str \| None` | Regex BR: `^\+55\d{10,11}$` |
| `password_hash` | TEXT | — | — | Nunca exposto; `password` no Create |
| `role` | TEXT CHECK | `role` | `Literal[...]` | Response only |
| `avatar_url` | TEXT | `avatar_url` | `HttpUrl \| None` | |
| `is_active` | BOOLEAN | `is_active` | `bool` | Response only |
| `last_login_at` | TIMESTAMPTZ | `last_login_at` | `datetime \| None` | Response only |
| `created_at` | TIMESTAMPTZ | `created_at` | `datetime` | Response only |

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal
from uuid import UUID
from datetime import datetime
import re

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(None, pattern=r"^\+55\d{10,11}$")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    consent_terms: bool = Field(...)
    consent_privacy: bool = Field(...)

    @field_validator("consent_terms", "consent_privacy")
    @classmethod
    def must_accept(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Aceite obrigatório dos termos")
        return v

class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = Field(None, pattern=r"^\+55\d{10,11}$")
    avatar_url: str | None = None

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone: str | None
    role: Literal["client", "professional", "admin"]
    avatar_url: str | None
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

### Inputs inválidos para testar
- `name` vazio, < 2 chars, > 100 chars
- `email` formato inválido, sem @, domínio inexistente
- `phone` sem +55, número curto/longo, letras
- `password` < 8 chars, > 128 chars
- `consent_terms=false`, `consent_privacy` ausente

---

## 2. Professionals (Módulo: Auth)

### DB → Schema mapping

| Coluna DB | Tipo DB | Campo Schema | Tipo Pydantic | Notas |
|-----------|---------|-------------|--------------|-------|
| `id` | UUID FK | `id` | `uuid.UUID` | Response only |
| `bio` | TEXT | `bio` | `str \| None` | max_length=1000 |
| `location` | GEOMETRY | `latitude`, `longitude` | `float` | Convertido no endpoint |
| `service_radius_km` | FLOAT | `service_radius_km` | `float` | gt=0, le=200 |
| `hourly_rate_cents` | INT | `hourly_rate_cents` | `int \| None` | gt=0 |
| `reputation_score` | FLOAT | `reputation_score` | `float` | Response only, ge=0, le=5 |
| `completed_jobs` | INT | `completed_jobs` | `int` | Response only |
| `is_verified` | BOOLEAN | `is_verified` | `bool` | Response only |
| `cancel_rate` | FLOAT | `cancel_rate` | `float` | Response only, ge=0, le=1 |
| `profile_embedding` | vector(1536) | — | — | Interno, nunca exposto |
| `verified_at` | TIMESTAMPTZ | `verified_at` | `datetime \| None` | Response only |

```python
class ProfessionalBase(BaseModel):
    bio: str | None = Field(None, max_length=1000)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    service_radius_km: float = Field(20.0, gt=0, le=200)
    hourly_rate_cents: int | None = Field(None, gt=0)

class ProfessionalCreate(UserBase, ProfessionalBase):
    password: str = Field(..., min_length=8, max_length=128)
    consent_terms: bool = Field(...)
    consent_privacy: bool = Field(...)
    category_ids: list[UUID] = Field(..., min_length=1, max_length=10)
    document_type: Literal["cpf", "cnpj"]
    # document_file enviado via multipart, não no JSON

    @field_validator("consent_terms", "consent_privacy")
    @classmethod
    def must_accept(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Aceite obrigatório dos termos")
        return v

class ProfessionalUpdate(BaseModel):
    bio: str | None = Field(None, max_length=1000)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    service_radius_km: float | None = Field(None, gt=0, le=200)
    hourly_rate_cents: int | None = Field(None, gt=0)

class ProfessionalResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    bio: str | None
    latitude: float
    longitude: float
    service_radius_km: float
    hourly_rate_cents: int | None
    completed_jobs: int
    reputation_score: float
    cancel_rate: float
    is_verified: bool
    verified_at: datetime | None
    categories: list["CategoryResponse"]

    model_config = {"from_attributes": True}
```

### Inputs inválidos para testar
- `latitude` > 90, < -90; `longitude` > 180
- `service_radius_km` = 0, negativo, > 200
- `hourly_rate_cents` = 0, negativo
- `category_ids` vazio, > 10 itens, UUID inválido
- `bio` > 1000 chars
- `document_type` valor inválido

---

## 3. Categories (Módulo: Pedidos/Geral)

```python
class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    color: str  # Hex color (#RRGGBB) — virá do campo `color` da tabela `categories`
    parent_id: UUID | None
    sort_order: int
    is_active: bool
    children: list["CategoryResponse"] = []

    model_config = {"from_attributes": True}

class CategoryCreate(BaseModel):  # Admin only
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., pattern=r"^[a-z0-9-]+$", max_length=100)
    color: str = Field("#1a9878", pattern=r"^#[0-9a-fA-F]{6}$")
    parent_id: UUID | None = None
    sort_order: int = Field(0, ge=0)

class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    slug: str | None = Field(None, pattern=r"^[a-z0-9-]+$")
    color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    parent_id: UUID | None = None
    sort_order: int | None = Field(None, ge=0)
    is_active: bool | None = None
```

### Inputs inválidos para testar
- `slug` com espaços, caracteres especiais, uppercase
- `name` vazio, > 100 chars
- `sort_order` negativo
- `color` formato inválido: `"red"`, `"#gg0000"` (chars inválidos), `"123456"` (sem `#`), `"#12345"` (5 dígitos)

---

## 4. Requests (Módulo: Pedidos)

### DB → Schema mapping

| Coluna DB | Tipo DB | Campo Schema | Tipo Pydantic | Notas |
|-----------|---------|-------------|--------------|-------|
| `id` | UUID | `id` | `UUID` | Response only |
| `client_id` | UUID FK | `client_id` | `UUID` | Response only (extraído do JWT) |
| `category_id` | UUID FK | `category_id` | `UUID` | |
| `title` | TEXT NOT NULL | `title` | `str` | min_length=5, max_length=200 |
| `description` | TEXT | `description` | `str \| None` | max_length=2000 |
| `location` | GEOMETRY | `latitude`, `longitude` | `float` | |
| `urgency` | TEXT CHECK | `urgency` | `Literal[...]` | |
| `budget_cents` | INT | `budget_cents` | `int \| None` | gt=0 |
| `status` | TEXT CHECK | `status` | `Literal[...]` | Response only |
| `ai_complexity` | TEXT | `ai_complexity` | `str \| None` | Response only |
| `ai_urgency` | TEXT | `ai_urgency` | `str \| None` | Response only |
| `ai_specialties` | TEXT[] | `ai_specialties` | `list[str]` | Response only |
| `created_at` | TIMESTAMPTZ | `created_at` | `datetime` | Response only |

```python
class RequestBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str | None = Field(None, max_length=2000)
    urgency: Literal["immediate", "scheduled", "flexible"]

class RequestCreate(RequestBase):
    category_id: UUID
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    budget_cents: int | None = Field(None, gt=0)

class RequestUpdate(BaseModel):
    title: str | None = Field(None, min_length=5, max_length=200)
    description: str | None = Field(None, max_length=2000)
    urgency: Literal["immediate", "scheduled", "flexible"] | None = None
    budget_cents: int | None = Field(None, gt=0)

class RequestResponse(RequestBase):
    id: UUID
    client_id: UUID
    category: CategoryResponse
    latitude: float
    longitude: float
    budget_cents: int | None
    status: Literal["open", "matched", "in_progress", "done", "cancelled"]
    ai_complexity: Literal["simple", "medium", "complex"] | None
    ai_urgency: Literal["low", "medium", "high"] | None
    ai_specialties: list[str]
    images: list["RequestImageResponse"]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### Inputs inválidos para testar
- `title` < 5 chars, > 200 chars
- `description` > 2000 chars
- `urgency` valor inválido (ex: "urgent")
- `budget_cents` = 0, negativo
- `category_id` UUID inválido
- `latitude`/`longitude` fora de range

---

## 5. Request Images (Módulo: Pedidos)

```python
class RequestImageResponse(BaseModel):
    id: UUID
    url: str
    content_type: Literal["image/jpeg", "image/png", "image/webp"]
    size_bytes: int
    analyzed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
```

> Upload via multipart — validação de content_type e size no endpoint, não no schema JSON.

---

## 6. Bids (Módulo: Bids/Contratos)

### DB → Schema mapping

| Coluna DB | Tipo DB | Campo Schema | Tipo Pydantic | Notas |
|-----------|---------|-------------|--------------|-------|
| `id` | UUID | `id` | `UUID` | Response only |
| `request_id` | UUID FK | `request_id` | `UUID` | Create only |
| `professional_id` | UUID FK | `professional_id` | `UUID` | Response only (JWT) |
| `message` | TEXT | `message` | `str \| None` | max_length=500 |
| `price_cents` | INT NOT NULL | `price_cents` | `int` | gt=0 |
| `estimated_hours` | INT | `estimated_hours` | `int \| None` | gt=0 |
| `status` | TEXT CHECK | `status` | `Literal[...]` | Response/Update |
| `created_at` | TIMESTAMPTZ | `created_at` | `datetime` | Response only |

```python
class BidBase(BaseModel):
    message: str | None = Field(None, max_length=500)
    price_cents: int = Field(..., gt=0)
    estimated_hours: int | None = Field(None, gt=0)

class BidCreate(BidBase):
    request_id: UUID

class BidUpdate(BaseModel):
    status: Literal["accepted", "rejected"]

class BidResponse(BidBase):
    id: UUID
    request_id: UUID
    professional_id: UUID
    professional_name: str  # computed: JOIN professionals/users
    status: Literal["pending", "accepted", "rejected", "cancelled"]
    created_at: datetime

    model_config = {"from_attributes": True}
```

### Inputs inválidos para testar
- `price_cents` = 0, negativo, ausente
- `estimated_hours` = 0, negativo
- `message` > 500 chars
- `request_id` UUID inválido
- `status` no Update: valor inválido (ex: "pending", "cancelled")

---

## 7. Contracts (Módulo: Bids/Contratos)

```python
class ContractResponse(BaseModel):
    id: UUID
    request_id: UUID
    professional_id: UUID
    client_id: UUID
    agreed_cents: int
    status: Literal["active", "payment_confirmed", "completed",
                    "disputed", "refunded", "partially_refunded", "cancelled"]
    started_at: datetime
    payment_confirmed_at: datetime | None
    payout_scheduled_at: datetime | None
    payout_completed_at: datetime | None
    completed_at: datetime | None
    professional: ProfessionalResponse  # nested
    dispute: "DisputeResponse | None"   # nested se existir

    model_config = {"from_attributes": True}

class PaymentCreate(BaseModel):
    """Inicia pagamento de um contrato."""
    pass  # contract_id vem da URL path; sem body adicional necessário
```

> Contratos são criados automaticamente (aceite de bid) — sem schema Create.

---

## 8. Reviews (Módulo: Reviews/Reputação)

### DB → Schema mapping

| Coluna DB | Tipo DB | Campo Schema | Tipo Pydantic | Notas |
|-----------|---------|-------------|--------------|-------|
| `id` | UUID | `id` | `UUID` | Response only |
| `contract_id` | UUID FK | `contract_id` | `UUID` | Create only |
| `rating` | INT CHECK 1-5 | `rating` | `int` | ge=1, le=5 |
| `text` | TEXT NOT NULL | `text` | `str` | min_length=10, max_length=2000 |
| `score_*` | FLOAT | `score_*` | `float \| None` | Response only (NLP) |
| `is_authentic` | BOOLEAN | `is_authentic` | `bool` | Response only |

```python
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=10, max_length=2000)

class ReviewCreate(ReviewBase):
    contract_id: UUID

class ReviewResponse(ReviewBase):
    id: UUID
    contract_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    score_punctuality: float | None
    score_quality: float | None
    score_cleanliness: float | None
    score_communication: float | None
    is_authentic: bool
    created_at: datetime

    model_config = {"from_attributes": True}
```

### Inputs inválidos para testar
- `rating` = 0, 6, negativo, float
- `text` < 10 chars, > 2000 chars, vazio
- `contract_id` UUID inválido, contrato não completado

---

## 9. Messages (Módulo: Chat)

```python
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)

class MessageResponse(BaseModel):
    id: UUID
    contract_id: UUID
    sender_id: UUID
    sender_name: str  # computed: JOIN users
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}

class MessageQuery(BaseModel):
    """Query params para paginação cursor-based."""
    cursor: datetime | None = None
    limit: int = Field(50, ge=1, le=100)
```

### Inputs inválidos para testar
- `content` vazio, > 5000 chars
- `limit` = 0, negativo, > 100
- `cursor` formato de data inválido

---

## 10. Notifications (Módulo: Painéis)

```python
NOTIFICATION_TYPES = Literal[
    "bid_received", "bid_accepted", "bid_rejected",
    "payment_confirmed", "payout_completed",
    "new_message", "review_request",
    "dispute_opened", "dispute_response", "dispute_resolved",
    "professional_verified", "professional_rejected",
    "account_warning"
]

class NotificationResponse(BaseModel):
    id: UUID
    type: NOTIFICATION_TYPES
    payload: dict
    read_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}

class NotificationMarkRead(BaseModel):
    notification_ids: list[UUID] = Field(..., min_length=1, max_length=100)
```

### Inputs inválidos para testar
- `notification_ids` vazio, > 100, UUID inválidos

---

## 11. Disputes (Módulo: Bids/Contratos)

### DB → Schema mapping

| Coluna DB | Tipo DB | Campo Schema | Tipo Pydantic | Notas |
|-----------|---------|-------------|--------------|-------|
| `reason` | TEXT NOT NULL | `reason` | `str` | min_length=10, max_length=2000 |
| `category` | TEXT CHECK | `category` | `Literal[...]` | |
| `evidence_urls` | TEXT[] | `evidence_urls` | `list[HttpUrl]` | max 10 |
| `status` | TEXT CHECK | `status` | `Literal[...]` | Response only |
| `resolution` | TEXT CHECK | `resolution` | `Literal[...]` | Resolve only |
| `refund_percent` | INT CHECK 1-99 | `refund_percent` | `int \| None` | ge=1, le=99 |
| `response_deadline` | TIMESTAMPTZ | `response_deadline` | `datetime` | Response only |

```python
class DisputeCreate(BaseModel):
    reason: str = Field(..., min_length=10, max_length=2000)
    category: Literal["quality", "no_show", "overcharge", "damage", "other"]
    evidence_urls: list[str] = Field(default=[], max_length=10)

class DisputeResponseAction(BaseModel):
    """Parte contrária responde à disputa."""
    message: str = Field(..., min_length=10, max_length=2000)
    evidence_urls: list[str] = Field(default=[], max_length=10)
    proposed_resolution: str | None = Field(None, max_length=500)

class DisputeResolve(BaseModel):
    """Admin resolve a disputa."""
    resolution: Literal["refund_full", "refund_partial", "refund_denied"]
    refund_percent: int | None = Field(None, ge=1, le=99)
    admin_notes: str = Field(..., min_length=5, max_length=2000)

    @field_validator("refund_percent")
    @classmethod
    def validate_percent(cls, v, info):
        resolution = info.data.get("resolution")
        if resolution == "refund_partial" and v is None:
            raise ValueError("refund_percent obrigatório para reembolso parcial")
        if resolution != "refund_partial" and v is not None:
            raise ValueError("refund_percent só se aplica a reembolso parcial")
        return v

class DisputeDetailResponse(BaseModel):
    id: UUID
    contract_id: UUID
    opened_by_user_id: UUID
    reason: str
    category: str
    evidence_urls: list[str]
    status: Literal["opened", "under_review", "auto_escalated", "resolved"]
    resolution: Literal["refund_full", "refund_partial", "refund_denied"] | None
    refund_percent: int | None
    admin_notes: str | None
    response_message: str | None
    response_evidence_urls: list[str]
    proposed_resolution: str | None
    response_deadline: datetime
    responded_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

### Inputs inválidos para testar
- `reason` < 10 chars, > 2000 chars, vazio
- `category` valor inválido
- `evidence_urls` > 10 itens, URLs inválidas
- `resolution` inválida, `refund_partial` sem `refund_percent`
- `refund_percent` = 0, 100, negativo, presente com `refund_full`
- `admin_notes` < 5 chars
- `message` (response) vazio, < 10 chars

---

## 12. Commission Rates (Módulo: Bids/Contratos)

```python
class CommissionRateCreate(BaseModel):
    category_id: UUID | None = None  # NULL = taxa padrão
    percent: float = Field(..., gt=0, lt=100)
    effective_from: date = Field(default_factory=date.today)
    effective_until: date | None = None

    @field_validator("effective_until")
    @classmethod
    def end_after_start(cls, v, info):
        start = info.data.get("effective_from")
        if v is not None and start is not None and v <= start:
            raise ValueError("effective_until deve ser posterior a effective_from")
        return v

class CommissionRateResponse(BaseModel):
    id: UUID
    category_id: UUID | None
    percent: float
    effective_from: date
    effective_until: date | None

    model_config = {"from_attributes": True}
```

### Inputs inválidos para testar
- `percent` = 0, 100, negativo
- `effective_until` anterior a `effective_from`

---

## 13. Consent Logs (Módulo: LGPD)

```python
class ConsentPayload(BaseModel):
    """Embedded no cadastro, não é endpoint separado."""
    consent_terms: bool = Field(...)
    consent_privacy: bool = Field(...)

    @field_validator("consent_terms", "consent_privacy")
    @classmethod
    def must_accept(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Aceite obrigatório")
        return v

class ConsentResponse(BaseModel):
    id: UUID
    consent_type: Literal["terms", "privacy", "marketing"]
    version: str
    accepted_at: datetime

    model_config = {"from_attributes": True}
```

### Inputs inválidos para testar
- `consent_terms=false`, `consent_privacy=false`
- Campos ausentes

---

## 14. Push Subscriptions (Módulo: PWA)

```python
class PushKeysSchema(BaseModel):
    p256dh: str = Field(..., min_length=10)
    auth: str = Field(..., min_length=10)

class PushSubscribeCreate(BaseModel):
    endpoint: str = Field(..., min_length=10)
    keys: PushKeysSchema
    device_label: str | None = Field(None, max_length=100)

class PushSubscriptionResponse(BaseModel):
    id: UUID
    endpoint: str
    device_label: str | None
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None

    model_config = {"from_attributes": True}
```

### Inputs inválidos para testar
- `endpoint` vazio, < 10 chars
- `keys.p256dh` ausente, vazio
- `keys.auth` ausente, vazio
- `device_label` > 100 chars

---

## 15. Favorites (Módulo: Painéis)

```python
class FavoriteCreate(BaseModel):
    professional_id: UUID

class FavoriteResponse(BaseModel):
    id: UUID
    professional_id: UUID
    professional: ProfessionalResponse  # nested
    created_at: datetime

    model_config = {"from_attributes": True}
```

### Inputs inválidos para testar
- `professional_id` UUID inválido, profissional inexistente

---

## 16. Auth Schemas Extras (Módulo: Auth)

```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int  # segundos

class DeleteAccountRequest(BaseModel):
    password: str = Field(..., min_length=1)
```

### Inputs inválidos para testar
- `LoginRequest`: email inválido, password vazio
- `RefreshRequest`: refresh_token vazio
- `DeleteAccountRequest`: password vazio

---

## Resumo: Schemas por Módulo

| Módulo | Schemas |
|--------|---------|
| **Auth** | UserBase, UserCreate, UserUpdate, UserResponse, ProfessionalBase, ProfessionalCreate, ProfessionalUpdate, ProfessionalResponse, LoginRequest, RefreshRequest, TokenResponse, DeleteAccountRequest |
| **Pedidos** | RequestBase, RequestCreate, RequestUpdate, RequestResponse, RequestImageResponse, CategoryResponse, CategoryCreate, CategoryUpdate |
| **Bids/Contratos** | BidBase, BidCreate, BidUpdate, BidResponse, ContractResponse, PaymentCreate, DisputeCreate, DisputeResponseAction, DisputeResolve, DisputeDetailResponse, CommissionRateCreate, CommissionRateResponse |
| **Chat** | MessageCreate, MessageResponse, MessageQuery |
| **Reviews** | ReviewBase, ReviewCreate, ReviewResponse |
| **Painéis** | NotificationResponse, NotificationMarkRead, FavoriteCreate, FavoriteResponse |
| **LGPD** | ConsentPayload, ConsentResponse |
| **PWA** | PushSubscribeCreate, PushKeysSchema, PushSubscriptionResponse |
