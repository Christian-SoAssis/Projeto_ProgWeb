# Spec: bid-contract

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Envio de orçamento pelo profissional (Bid)

O sistema **SHALL** permitir ao profissional verificado responder a pedidos com `status='open'` enviando uma proposta de bid.

### Scenario 1 — Bid enviado com sucesso

- **GIVEN** que o profissional está autenticado com `is_verified=true` e o pedido tem `status='open'`
- **WHEN** o profissional envia `POST /bids` com `{ request_id, price_cents, message, estimated_hours }`
- **THEN** o sistema **MUST** criar o bid com `status='pending'`, notificar o cliente via WebSocket/push, retornar `201 Created`

### Scenario 2 — Profissional não verificado

- **GIVEN** que o profissional possui `is_verified=false`
- **WHEN** tenta enviar `POST /bids`
- **THEN** o sistema **MUST** retornar `403 Forbidden` com mensagem `"Verificação de conta pendente"`

### Scenario 3 — Pedido não está aberto

- **GIVEN** que o `request_id` existe mas tem `status != 'open'`
- **WHEN** o profissional tenta enviar bid
- **THEN** o sistema **MUST** retornar `409 Conflict` com mensagem `"Pedido não está disponível para bids"`

### Scenario 4 — Campo obrigatório ausente (validação Pydantic)

- **GIVEN** que o payload omite `price_cents` ou `request_id`
- **WHEN** a requisição é recebida pelo FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe por campo

### Scenario 5 — PostgreSQL indisponível

- **GIVEN** que o banco está inacessível
- **WHEN** o sistema tenta persistir o bid
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

### Scenario 6 — Profissional tenta enviar bid duplicado

- **GIVEN** que o profissional já enviou bid para o mesmo pedido
- **WHEN** tenta enviar novamente
- **THEN** o sistema **MUST** retornar `409 Conflict` com mensagem `"Você já enviou uma proposta para este pedido"`

---

## Requirement: Aceitação ou rejeição de bid pelo cliente

O sistema **SHALL** permitir ao cliente donos do pedido aceitar ou rejeitar bids recebidos.

### Scenario 1 — Cliente aceita bid

- **GIVEN** que o bid tem `status='pending'` e pertence a um pedido do cliente autenticado
- **WHEN** o cliente envia `PATCH /bids/:id` com `{ status: 'accepted' }`
- **THEN** o sistema **MUST** atualizar `bid.status='accepted'`, criar contrato automaticamente (ver Requirement: Criação automática de contrato), notificar profissional, retornar `200 OK`

### Scenario 2 — Cliente rejeita bid

- **GIVEN** que o bid tem `status='pending'`
- **WHEN** o cliente envia `PATCH /bids/:id` com `{ status: 'rejected' }`
- **THEN** o sistema **MUST** atualizar `bid.status='rejected'`, notificar profissional, retornar `200 OK`

### Scenario 3 — Cliente tenta operar bid de outro cliente

- **GIVEN** que o `bid_id` pertence a pedido de outro cliente
- **WHEN** o cliente autenticado envia `PATCH /bids/:id`
- **THEN** o sistema **MUST** retornar `403 Forbidden`

### Scenario 4 — Bid já aceito ou rejeitado

- **GIVEN** que o bid já tem `status != 'pending'`
- **WHEN** o cliente tenta alterar novamente
- **THEN** o sistema **MUST** retornar `409 Conflict` com mensagem `"Esta proposta já foi processada"`

### Scenario 5 — PostgreSQL indisponível durante aceitação

- **GIVEN** que o banco está inacessível
- **WHEN** a atualização do bid é tentada
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`; **MUST NOT** criar contrato parcial

---

## Requirement: Criação automática de contrato

O sistema **SHALL** criar um contrato de forma atômica no momento da aceitação de um bid.

### Scenario 1 — Contrato criado com sucesso

- **GIVEN** que o bid foi aceito e nenhum contrato ativo existe para o pedido
- **WHEN** a transação de aceitação é processada no banco
- **THEN** o sistema **MUST** criar registro em `contracts` com `status='active'`, `agreed_cents=bid.price_cents`; **MUST** atualizar `request.status='matched'`; a operação **MUST** ser executada dentro de uma única transação de banco (atômica)

### Scenario 2 — Falha transacional durante criação do contrato

- **GIVEN** que a escrita no banco falha no meio da transação (ex.: constraint violation)
- **WHEN** o banco reverte a transação
- **THEN** o sistema **MUST** garantir rollback completo (bid permanece `pending`, request permanece `open`); **MUST** retornar `500 Internal Server Error` sem deixar dados inconsistentes

---

## Requirement: Pagamento integrado via MercadoPago

O sistema **SHALL** processar pagamento ao concluir o serviço via MercadoPago com split-payment (marketplace mode).

### Scenario 1 — Pagamento iniciado pelo cliente

- **GIVEN** que o contrato tem `status='active'` e o cliente confirmou a conclusão do serviço
- **WHEN** o cliente inicia o pagamento via `POST /contracts/:id/payment`
- **THEN** o sistema **MUST** criar uma cobrança no MercadoPago com split: `(100-X)%` ao profissional, `X%` à plataforma; retornar URL de checkout ou preferência de pagamento PIX

### Scenario 2 — Webhook de confirmação de pagamento recebido

- **GIVEN** que o MercadoPago envia webhook com `status='approved'` para o endpoint `POST /webhooks/mercadopago`
- **WHEN** o sistema processa e valida a assinatura do webhook
- **THEN** o sistema **MUST** atualizar `contract.status='completed'`, liberar saldo ao profissional, habilitar fluxo de review, retornar `200 OK` ao MercadoPago

### Scenario 3 — Assinatura de webhook inválida

- **GIVEN** que o `X-Signature` do webhook não corresponde ao segredo configurado
- **WHEN** o sistema valida o webhook
- **THEN** o sistema **MUST** retornar `401 Unauthorized` e descartar o evento sem processar

### Scenario 4 — Pagamento recusado

- **GIVEN** que o MercadoPago envia webhook com `status='rejected'`
- **WHEN** o sistema processa o webhook
- **THEN** o sistema **MUST** manter `contract.status='active'`, notificar cliente para tentar novamente

### Scenario 5 — MercadoPago API indisponível

- **GIVEN** que a API do MercadoPago não responde em 10 s
- **WHEN** o sistema tenta criar a cobrança
- **THEN** o sistema **MUST** retornar `503 Service Unavailable` ao cliente; **MUST NOT** alterar o status do contrato

---

## Requirement: Disputa de contrato

O sistema **SHALL** suportar abertura de disputa em contratos ativos com encaminhamento para revisão pelo admin.

### Scenario 1 — Cliente abre disputa

- **GIVEN** que o contrato tem `status='active'` e pertence ao cliente autenticado
- **WHEN** o cliente envia `POST /contracts/:id/dispute` com `{ reason: '...' }`
- **THEN** o sistema **MUST** atualizar `contract.status='disputed'`, notificar admin, retornar `200 OK`

### Scenario 2 — Disputa em contrato já concluído ou cancelado

- **GIVEN** que o contrato tem `status='completed'` ou `status='cancelled'`
- **WHEN** o cliente tenta abrir disputa
- **THEN** o sistema **MUST** retornar `409 Conflict` com mensagem `"Disputa não pode ser aberta neste status"`

### Scenario 3 — Motivo da disputa ausente

- **GIVEN** que o campo `reason` é omitido ou vazio
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity`
