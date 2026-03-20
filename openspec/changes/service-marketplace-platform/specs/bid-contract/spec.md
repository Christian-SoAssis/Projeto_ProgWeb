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

O sistema **SHALL** processar pagamento ao concluir o serviço via MercadoPago com split-payment (marketplace mode), com comissão por categoria e repasse configurável.

### Comissão por categoria

> [!WARNING]
> **Valor temporário**: O percentual de comissão padrão de **5%** é provisório e será revisado após validação de mercado. A implementação **MUST** ler o percentual de uma tabela `commission_rates` configurável, nunca hardcoded.

| Categoria | Comissão (%) | Observação |
|---|---|---|
| **Padrão (todas)** | **5%** | ⚠️ Temporário — sujeito a revisão |
| _Futuro: categorias premium_ | _A definir_ | _Configurável por categoria via admin_ |

O sistema **MUST** armazenar as taxas na tabela `commission_rates` com campos: `category_id` (nullable = taxa padrão), `percent`, `effective_from`, `effective_until`. Ao processar um pagamento, **MUST** consultar a taxa ativa para a categoria do serviço; se não houver taxa específica, usar a taxa padrão.

### Lógica de split-payment

O split no MercadoPago Marketplace **MUST** ser configurado como:
- **Profissional recebe**: `agreed_cents × (1 - commission_percent / 100)`
- **Plataforma recebe**: `agreed_cents × (commission_percent / 100)`

O `marketplace_fee` (valor da plataforma em centavos) **MUST** ser enviado no campo `marketplace_fee` da preferência de pagamento do MercadoPago.

### Scenario 1 — Pagamento iniciado pelo cliente

- **GIVEN** que o contrato tem `status='active'` e o cliente confirmou a conclusão do serviço
- **WHEN** o cliente inicia o pagamento via `POST /contracts/:id/payment`
- **THEN** o sistema **MUST**:
  - Consultar `commission_rates` para a categoria do serviço (fallback para taxa padrão)
  - Calcular `marketplace_fee = agreed_cents × commission_percent / 100`
  - Criar preferência de pagamento no MercadoPago com `marketplace_fee` e `collector_id` do profissional
  - Retornar URL de checkout ou preferência de pagamento PIX

### Scenario 2 — Webhook de confirmação de pagamento recebido

- **GIVEN** que o MercadoPago envia webhook com `status='approved'` para `POST /webhooks/mercadopago`
- **WHEN** o sistema processa e valida a assinatura do webhook (`X-Signature` + segredo HMAC)
- **THEN** o sistema **MUST**:
  - Atualizar `contract.status='payment_confirmed'`
  - Registrar `payment_confirmed_at = NOW()`
  - Agendar repasse ao profissional para **D+2** (2 dias úteis após confirmação)
  - Habilitar fluxo de review para o cliente
  - Notificar profissional: `"Pagamento confirmado — repasse previsto para DD/MM/AAAA"`
  - Retornar `200 OK` ao MercadoPago

### Scenario 3 — Repasse ao profissional (D+2)

- **GIVEN** que o contrato tem `status='payment_confirmed'` e `payout_scheduled_at <= NOW()` e não há disputa aberta
- **WHEN** o job de repasse (cron diário) executa
- **THEN** o sistema **MUST**:
  - Atualizar `contract.status='completed'`
  - Registrar `payout_completed_at = NOW()`
  - Notificar profissional: `"Repasse de R$ X,XX liberado na sua conta"`

### Scenario 4 — Disputa aberta retém pagamento

- **GIVEN** que o contrato tem `status='payment_confirmed'` e uma disputa é aberta antes de D+2
- **WHEN** o job de repasse executa e detecta `contract.status='disputed'`
- **THEN** o sistema **MUST NOT** liberar o repasse; o saldo **MUST** permanecer retido até resolução da disputa:
  - Se `refund_full` → reembolso total ao cliente, profissional não recebe
  - Se `refund_partial` → reembolso parcial ao cliente, profissional recebe restante
  - Se `refund_denied` → repasse integral ao profissional, atualizar `contract.status='completed'`

### Scenario 5 — Assinatura de webhook inválida

- **GIVEN** que o `X-Signature` do webhook não corresponde ao segredo HMAC configurado
- **WHEN** o sistema valida o webhook
- **THEN** o sistema **MUST** retornar `401 Unauthorized`, logar o evento como alerta de segurança, descartar sem processar

### Scenario 6 — Pagamento recusado

- **GIVEN** que o MercadoPago envia webhook com `status='rejected'`
- **WHEN** o sistema processa o webhook
- **THEN** o sistema **MUST** manter `contract.status='active'`, notificar cliente: `"Pagamento não aprovado — tente novamente ou use outro método"`

### Scenario 7 — MercadoPago API indisponível

- **GIVEN** que a API do MercadoPago não responde em 10s
- **WHEN** o sistema tenta criar a cobrança
- **THEN** o sistema **MUST** retornar `503 Service Unavailable` ao cliente; **MUST NOT** alterar o status do contrato

### Scenario 8 — Webhook com payment_id duplicado (idempotência)

- **GIVEN** que o MercadoPago reenvia webhook com mesmo `payment_id` já processado
- **WHEN** o sistema recebe o webhook
- **THEN** o sistema **MUST** retornar `200 OK` sem reprocessar (idempotente); **MUST NOT** duplicar registros

---

## Requirement: Disputa de contrato — Fluxo completo

O sistema **SHALL** suportar um fluxo de disputa completo com abertura por qualquer parte (cliente ou profissional), prazo de resposta, arbitragem pelo admin e critérios claros de reembolso. O fluxo **MUST** gerar notificações em cada transição de estado.

### Estados da disputa

```
opened → awaiting_response (72h) → under_review (admin) → resolved (refund_full | refund_partial | refund_denied)
                                  ↘ auto_escalated (se 72h expiram sem resposta)
```

### Scenario 1 — Cliente abre disputa

- **GIVEN** que o contrato tem `status='active'` e pertence ao cliente autenticado
- **WHEN** o cliente envia `POST /contracts/:id/dispute` com `{ reason, category, evidence_urls[] }`
- **THEN** o sistema **MUST**:
  - Criar registro em `disputes` com `status='opened'`, `opened_by='client'`, `response_deadline = NOW() + 72h`
  - Atualizar `contract.status='disputed'`
  - Notificar o profissional via WebSocket/push: `"O cliente abriu uma disputa. Você tem 72h para responder."`
  - Notificar o admin via painel: nova disputa pendente
  - Retornar `201 Created` com `dispute_id` e `response_deadline`

### Scenario 2 — Profissional abre disputa

- **GIVEN** que o contrato tem `status='active'` e pertence ao profissional autenticado
- **WHEN** o profissional envia `POST /contracts/:id/dispute` com `{ reason, category, evidence_urls[] }`
- **THEN** o sistema **MUST** executar o mesmo fluxo do Scenario 1 com `opened_by='professional'`, notificando o cliente para responder em 72h

### Scenario 3 — Parte contrária responde dentro de 72h

- **GIVEN** que a disputa tem `status='opened'` e o `response_deadline` não expirou
- **WHEN** a parte contrária envia `POST /disputes/:id/response` com `{ message, evidence_urls[], proposed_resolution }`
- **THEN** o sistema **MUST**:
  - Salvar a resposta vinculada à disputa
  - Atualizar `dispute.status='under_review'`
  - Notificar admin: `"Disputa #ID pronta para arbitragem — ambas as partes se manifestaram"`
  - Notificar a parte que abriu: `"A outra parte respondeu à sua disputa"`
  - Retornar `200 OK`

### Scenario 4 — Prazo de 72h expira sem resposta

- **GIVEN** que a disputa tem `status='opened'` e `NOW() > response_deadline`
- **WHEN** o job de expiração de disputas (cron) executa
- **THEN** o sistema **MUST**:
  - Atualizar `dispute.status='auto_escalated'`
  - Notificar admin: `"Disputa #ID escalada automaticamente — sem resposta em 72h"`
  - Notificar a parte não responsiva: `"O prazo de resposta expirou. A disputa foi encaminhada para análise."`

### Scenario 5 — Admin resolve com reembolso total

- **GIVEN** que a disputa tem `status='under_review'` ou `status='auto_escalated'`
- **WHEN** admin envia `PATCH /admin/disputes/:id` com `{ resolution: 'refund_full', admin_notes }` 
- **THEN** o sistema **MUST**:
  - Atualizar `dispute.status='resolved'`, `dispute.resolution='refund_full'`
  - Acionar reembolso total via MercadoPago API (100% do `contract.agreed_cents`)
  - Atualizar `contract.status='refunded'`
  - Notificar cliente: `"Disputa resolvida — reembolso total aprovado"`
  - Notificar profissional: `"Disputa resolvida — reembolso total ao cliente"`

### Scenario 6 — Admin resolve com reembolso parcial

- **GIVEN** que a disputa está em `under_review` ou `auto_escalated`
- **WHEN** admin envia `PATCH /admin/disputes/:id` com `{ resolution: 'refund_partial', refund_percent, admin_notes }`
- **THEN** o sistema **MUST**:
  - Validar `1 <= refund_percent <= 99`
  - Atualizar `dispute.status='resolved'`, `dispute.resolution='refund_partial'`, `dispute.refund_percent`
  - Acionar reembolso parcial via MercadoPago API (`refund_percent%` do `agreed_cents`)
  - Atualizar `contract.status='partially_refunded'`
  - Notificar ambas as partes com o percentual e motivo

### Scenario 7 — Admin nega reembolso

- **GIVEN** que a disputa está em `under_review` ou `auto_escalated`
- **WHEN** admin envia `PATCH /admin/disputes/:id` com `{ resolution: 'refund_denied', admin_notes }`
- **THEN** o sistema **MUST**:
  - Atualizar `dispute.status='resolved'`, `dispute.resolution='refund_denied'`
  - Manter `contract.status='active'` (serviço deve continuar ou ser concluído)
  - Notificar ambas as partes: `"Disputa analisada — reembolso não concedido"` com `admin_notes`

### Scenario 8 — Disputa em contrato já concluído, cancelado ou já disputado

- **GIVEN** que o contrato tem `status` em `['completed', 'cancelled', 'disputed', 'refunded']`
- **WHEN** qualquer parte tenta abrir disputa
- **THEN** o sistema **MUST** retornar `409 Conflict` com mensagem `"Disputa não pode ser aberta neste status"`

### Scenario 9 — Motivo ou categoria ausente

- **GIVEN** que o campo `reason` é omitido/vazio ou `category` não é uma das opções válidas (`quality`, `no_show`, `overcharge`, `damage`, `other`)
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity`

### Scenario 10 — Usuário não-admin tenta resolver disputa

- **GIVEN** que o token JWT pertence a um usuário com `role != 'admin'`
- **WHEN** envia `PATCH /admin/disputes/:id`
- **THEN** o sistema **MUST** retornar `403 Forbidden`

### Scenario 11 — Consulta de disputas pelo admin

- **GIVEN** que admin autenticado deseja listar disputas
- **WHEN** envia `GET /admin/disputes?status=opened|under_review|auto_escalated`
- **THEN** o sistema **MUST** retornar lista paginada com `dispute_id`, `contract_id`, `opened_by`, `reason`, `category`, `status`, `response_deadline`, `created_at`

