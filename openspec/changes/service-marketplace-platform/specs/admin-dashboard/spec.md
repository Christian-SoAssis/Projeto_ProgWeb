# Spec: admin-dashboard

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Aprovação e rejeição de profissionais

O sistema **SHALL** permitir ao admin visualizar profissionais pendentes de verificação e aprovar ou rejeitar com justificativa obrigatória em caso de rejeição.

### Scenario 1 — Listagem de profissionais pendentes

- **GIVEN** que o usuário autenticado possui `role='admin'`
- **WHEN** acessa `GET /admin/professionals?is_verified=false`
- **THEN** o sistema **MUST** retornar lista paginada de profissionais com `is_verified=false`, incluindo URLs dos documentos de verificação no S3/MinIO

### Scenario 2 — Aprovação de profissional

- **GIVEN** que o profissional tem `is_verified=false` e o solicitante é admin
- **WHEN** admin envia `PATCH /admin/professionals/:id` com `{ status: 'verified' }`
- **THEN** o sistema **MUST** atualizar `is_verified=true`, enfileirar indexação no Typesense, enviar notificação ao profissional (`type='account_verified'`), retornar `200 OK`

### Scenario 3 — Rejeição de profissional com motivo

- **GIVEN** que o profissional está aguardando aprovação
- **WHEN** admin envia `PATCH /admin/professionals/:id` com `{ status: 'rejected', reason: '...' }`
- **THEN** o sistema **MUST** manter `is_verified=false`, registrar o motivo no histórico, notificar o profissional com o motivo da rejeição, retornar `200 OK`

### Scenario 4 — Rejeição sem motivo

- **GIVEN** que o payload não inclui o campo `reason` ou está vazio
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com mensagem `"O campo 'reason' é obrigatório para rejeição"`

### Scenario 5 — Acesso de usuário não-admin

- **GIVEN** que o token JWT pertence a um usuário com `role != 'admin'`
- **WHEN** qualquer requisição é feita a `GET|PATCH /admin/*`
- **THEN** o sistema **MUST** retornar `403 Forbidden`; **MUST NOT** expor dados de outros usuários

### Scenario 6 — PostgreSQL indisponível durante aprovação

- **GIVEN** que o banco está inacessível
- **WHEN** o sistema tenta atualizar `is_verified`
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`; **MUST NOT** enfileirar indexação no Typesense sem garantia de que a atualização foi persistida

---

## Requirement: Monitoramento de flags de fraude

O sistema **SHALL** exibir ao admin alertas de desintermediação e reviews inautênticas para revisão e ação manual.

### Scenario 1 — Visualização de alertas de desintermediação

- **GIVEN** que o admin está autenticado
- **WHEN** acessa `GET /admin/flags?type=disintermediation`
- **THEN** o sistema **MUST** retornar lista paginada de flags com `contract_id`, `message_id`, trecho da mensagem suspeita, identificação dos usuários envolvidos e `created_at`

### Scenario 2 — Visualização de reviews suspeitas

- **GIVEN** que existem reviews com `is_authentic=false`
- **WHEN** admin acessa `GET /admin/flags?type=fake_review`
- **THEN** o sistema **MUST** retornar reviews marcadas com `is_authentic=false` para revisão manual, incluindo `review_id`, `text`, `rating` e dados do contrato

### Scenario 3 — Admin resolve flag manualmente

- **GIVEN** que uma flag está em estado `pending`
- **WHEN** admin envia `PATCH /admin/flags/:id` com `{ resolution: 'dismissed' | 'actioned', notes: '...' }`
- **THEN** o sistema **MUST** atualizar o estado da flag, registrar `resolved_by`, `resolved_at` e `notes`, retornar `200 OK`

### Scenario 4 — Tipo de flag inexistente

- **GIVEN** que o parâmetro `type` enviado não corresponde a nenhum tipo válido
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com os valores válidos aceitos

### Scenario 5 — PostgreSQL indisponível durante listagem de flags

- **GIVEN** que o banco está inacessível
- **WHEN** a query é executada
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

---

## Requirement: Dashboard de métricas gerais da plataforma

O sistema **SHALL** exibir ao admin KPIs consolidados da plataforma com atualização periódica (cache de 1 h no Redis).

### Scenario 1 — KPIs retornados com sucesso

- **GIVEN** que o admin está autenticado e o cache Redis está disponível
- **WHEN** acessa `GET /admin/metrics`
- **THEN** o sistema **MUST** retornar `{ mau, total_contracts_month, gmv_cents, match_conversion_rate, avg_matching_latency_ms, open_flags_count }`; os dados **SHOULD** ser servidos do cache Redis se calculados há menos de 1 h

### Scenario 2 — Cache Redis indisponível

- **GIVEN** que o Redis está inacessível
- **WHEN** o endpoint de métricas é acessado
- **THEN** o sistema **MUST** calcular os KPIs diretamente via query ao PostgreSQL e retornar normalmente; **MUST** logar a falha de cache; a latência da resposta **MAY** ser maior que o habitual

### Scenario 3 — PostgreSQL indisponível

- **GIVEN** que o banco está inacessível e o cache Redis também não possui dados válidos
- **WHEN** o endpoint é acessado
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

---

## Requirement: Gestão de categorias de serviço

O sistema **SHALL** permitir ao admin criar, editar e desativar categorias de serviço.

### Scenario 1 — Criação de nova categoria

- **GIVEN** que o admin está autenticado e o payload é válido
- **WHEN** envia `POST /admin/categories` com `{ name, slug, parent_id? }`
- **THEN** o sistema **MUST** criar a categoria no banco, retornar `201 Created`; se `parent_id` for fornecido, **MUST** validar que a categoria pai existe

### Scenario 2 — Slug duplicado

- **GIVEN** que já existe categoria com o mesmo `slug`
- **WHEN** o admin tenta criar nova categoria com esse slug
- **THEN** o sistema **MUST** retornar `409 Conflict` com mensagem `"Slug já em uso"`

### Scenario 3 — Campo obrigatório ausente

- **GIVEN** que o payload omite `name` ou `slug`
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe por campo

### Scenario 4 — Desativação de categoria com pedidos ativos vinculados

- **GIVEN** que existem pedidos com `status IN ('open', 'matched', 'in_progress')` vinculados à categoria
- **WHEN** o admin tenta `DELETE /admin/categories/:id`
- **THEN** o sistema **MUST** retornar `409 Conflict` com mensagem `"Categoria possui pedidos ativos vinculados. Reatribua antes de desativar"`; **MUST NOT** excluir a categoria
