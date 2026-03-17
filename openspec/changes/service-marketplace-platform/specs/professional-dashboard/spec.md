# Spec: professional-dashboard

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Visualização de bids pendentes e agenda de contratos

O sistema **SHALL** exibir ao profissional autenticado seus bids pendentes e agenda de contratos ativos, segmentados por status.

### Scenario 1 — Listagem de bids pendentes

- **GIVEN** que o profissional está autenticado com `is_verified=true` e possui bids com `status='pending'`
- **WHEN** envia `GET /professionals/me/bids?status=pending`
- **THEN** o sistema **MUST** retornar lista de bids pendentes com detalhes do pedido (`title`, `category`, `urgency`, `budget_cents`) e dados básicos do cliente

### Scenario 2 — Agenda de contratos ativos

- **GIVEN** que o profissional possui contratos com `status='active'`
- **WHEN** envia `GET /professionals/me/contracts?status=active`
- **THEN** o sistema **MUST** retornar contratos ativos com `client_name`, `agreed_cents`, `started_at` e status do pedido

### Scenario 3 — Profissional sem bids ou contratos

- **GIVEN** que o profissional não possui registros com o status filtrado
- **WHEN** a listagem é solicitada
- **THEN** o sistema **MUST** retornar lista vazia `[]` com `200 OK`; **MUST NOT** retornar `404`

### Scenario 4 — Profissional não verificado tenta acessar dashboard de bids

- **GIVEN** que o profissional possui `is_verified=false`
- **WHEN** tenta acessar `GET /professionals/me/bids`
- **THEN** o sistema **MUST** retornar `403 Forbidden` com mensagem `"Conta aguardando verificação"`

### Scenario 5 — PostgreSQL indisponível

- **GIVEN** que o banco está inacessível
- **WHEN** a query de bids ou contratos é executada
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

---

## Requirement: Métricas de performance do profissional

O sistema **SHALL** exibir métricas de earnings, taxa de conversão, `reputation_score` e scores por dimensão para o profissional autenticado.

### Scenario 1 — Métricas disponíveis

- **GIVEN** que o profissional possui contratos concluídos e reviews processadas
- **WHEN** envia `GET /professionals/me/metrics`
- **THEN** o sistema **MUST** retornar `{ total_earned_cents, conversion_rate, avg_rating, completed_jobs, reputation_score, reputation_dimensions: { punctuality, quality, cleanliness, communication } }`

### Scenario 2 — Profissional sem histórico suficiente

- **GIVEN** que o profissional ainda não concluiu contratos ou não possui reviews
- **WHEN** envia `GET /professionals/me/metrics`
- **THEN** o sistema **MUST** retornar os campos zerados ou `null` conforme aplicável; **MUST NOT** retornar erro; a UI **SHOULD** exibir estado "em branco" com orientação ao profissional

### Scenario 3 — PostgreSQL indisponível durante cálculo de métricas

- **GIVEN** que o banco está inacessível
- **WHEN** a query de métricas é executada
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

---

## Requirement: Atualização de perfil do profissional

O sistema **SHALL** permitir ao profissional atualizar `bio`, `location`, `service_radius_km` e `hourly_rate_cents` via PATCH parcial.

### Scenario 1 — Atualização bem-sucedida com nova localização

- **GIVEN** que o profissional está autenticado e os campos enviados são válidos
- **WHEN** envia `PATCH /professionals/me` com `{ location: { lat, lng }, bio: "..." }`
- **THEN** o sistema **MUST** atualizar os campos no PostgreSQL; se `location` mudou, **MUST** enfileirar job para regenerar embedding e atualizar índice no Typesense; retornar perfil atualizado com `200 OK`

### Scenario 2 — Campo inválido (validação Pydantic)

- **GIVEN** que o payload contém campo com tipo incorreto (ex.: `hourly_rate_cents: "abc"`)
- **WHEN** a requisição é validada pelo FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe por campo; **MUST NOT** persistir alterações parciais

### Scenario 3 — Coordenadas de localização fora do intervalo válido

- **GIVEN** que `lat` está fora de `[-90, 90]` ou `lng` fora de `[-180, 180]`
- **WHEN** a requisição é validada
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe no campo `location`

### Scenario 4 — PostgreSQL indisponível durante atualização

- **GIVEN** que o banco está inacessível
- **WHEN** o PATCH é processado
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`; **MUST NOT** enfileirar job de reindexação sem garantia de persistência

### Scenario 5 — Falha de validação no front-end (raio de atendimento)

- **GIVEN** que o formulário de edição de perfil no front-end exige `service_radius_km` entre 1 e 200 km
- **WHEN** o usuário submete valor fora desse range
- **THEN** a UI (shadcn/ui + React Hook Form) **MUST** exibir erro inline sem fazer requisição ao backend; se a requisição chegar mesmo assim ao backend, Pydantic v2 **MUST** retornar `422`

---

## Requirement: Histórico de earnings (pagamentos recebidos)

O sistema **SHALL** exibir histórico de pagamentos recebidos pelo profissional com filtro por período.

### Scenario 1 — Histórico filtrado por período

- **GIVEN** que o profissional possui contratos concluídos com pagamento confirmado
- **WHEN** envia `GET /professionals/me/earnings?from=2024-01&to=2024-03`
- **THEN** o sistema **MUST** retornar lista de pagamentos no período com `contract_id`, `client_name`, `amount_cents`, `paid_at` e um campo `total_period_cents` com o somatório

### Scenario 2 — Período sem pagamentos

- **GIVEN** que não há contratos concluídos no período especificado
- **WHEN** a query é executada
- **THEN** o sistema **MUST** retornar lista vazia `[]` com `total_period_cents: 0`

### Scenario 3 — Formato de data inválido

- **GIVEN** que o parâmetro `from` ou `to` não está no formato `YYYY-MM`
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe no parâmetro de data

### Scenario 4 — PostgreSQL indisponível

- **GIVEN** que o banco está inacessível
- **WHEN** a query de earnings é executada
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`
