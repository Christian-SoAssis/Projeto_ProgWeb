# Spec: client-dashboard

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Visualização de pedidos ativos e histórico

O sistema **SHALL** exibir ao cliente autenticado seus pedidos em curso e histórico completo, paginados.

### Scenario 1 — Listagem de pedidos ativos

- **GIVEN** que o cliente está autenticado e possui pedidos com `status IN ('open', 'matched', 'in_progress')`
- **WHEN** envia `GET /requests?status=open,matched,in_progress`
- **THEN** o sistema **MUST** retornar apenas os pedidos do próprio cliente com esses status, incluindo contagem de bids recebidos; **MUST NOT** expor pedidos de outros clientes

### Scenario 2 — Histórico de pedidos concluídos (paginação)

- **GIVEN** que o cliente possui pedidos com `status='done'`
- **WHEN** envia `GET /requests?status=done&page=1&limit=20`
- **THEN** o sistema **MUST** retornar histórico paginado com metadados de paginação (`total`, `page`, `limit`)

### Scenario 3 — Cliente sem pedidos

- **GIVEN** que o cliente ainda não criou nenhum pedido
- **WHEN** envia `GET /requests`
- **THEN** o sistema **MUST** retornar lista vazia `[]` com `200 OK`; **MUST NOT** retornar `404`

### Scenario 4 — PostgreSQL indisponível

- **GIVEN** que o banco está inacessível
- **WHEN** a query de listagem é executada
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

### Scenario 5 — Parâmetro `status` inválido

- **GIVEN** que o cliente envia `status=inexistente`
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe no parâmetro `status`

---

## Requirement: Lista de profissionais favoritos

O sistema **SHALL** permitir ao cliente salvar e visualizar profissionais favoritos, sem limite de quantidade.

### Scenario 1 — Adicionar profissional aos favoritos

- **GIVEN** que o cliente está autenticado e o `professional_id` existe e está verificado
- **WHEN** o cliente envia `POST /favorites` com `{ professional_id }`
- **THEN** o sistema **MUST** registrar o favorito, retornar `201 Created`

### Scenario 2 — Profissional já favoritado

- **GIVEN** que o profissional já está na lista de favoritos do cliente
- **WHEN** o cliente envia nova requisição `POST /favorites` com o mesmo `professional_id`
- **THEN** o sistema **MUST** retornar `409 Conflict` com mensagem `"Profissional já está nos favoritos"`

### Scenario 3 — Listar favoritos com scores atualizados

- **GIVEN** que o cliente possui favoritos cadastrados
- **WHEN** envia `GET /favorites`
- **THEN** o sistema **MUST** retornar lista de profissionais favoritos com `reputation_score`, `avg_rating` e `completed_jobs` atualizados

### Scenario 4 — Remover favorito

- **GIVEN** que o `professional_id` está nos favoritos do cliente
- **WHEN** o cliente envia `DELETE /favorites/:professional_id`
- **THEN** o sistema **MUST** remover o favorito, retornar `204 No Content`

### Scenario 5 — Profissional do favorito foi desativado

- **GIVEN** que um profissional favorito teve conta desativada pelo admin
- **WHEN** o cliente acessa `GET /favorites`
- **THEN** o sistema **SHOULD** retornar o favorito com um campo `is_active: false` para que a UI exiba estado adequado; **MUST NOT** omitir o item da lista silenciosamente

---

## Requirement: Notificações do cliente

O sistema **SHALL** entregar notificações em tempo real (WebSocket) e push (PWA) sobre eventos relevantes para o cliente.

### Scenario 1 — Notificação de bid recebido

- **GIVEN** que um profissional enviou bid para o pedido do cliente
- **WHEN** o bid é criado no banco
- **THEN** o sistema **MUST** criar notificação `type='bid_received'` com `payload: { bid_id, professional_name, price_cents }`; **MUST** entregá-la via WebSocket se cliente estiver online; **MUST** entregá-la via push PWA se offline

### Scenario 2 — Notificação de mensagem no chat

- **GIVEN** que o profissional enviou mensagem no chat de um contrato ativo
- **WHEN** a mensagem é persistida
- **THEN** o sistema **MUST** criar notificação `type='message'` se o cliente estiver offline; **MUST NOT** criar notificação duplicada se o cliente estiver com o chat aberto (ativo no WebSocket)

### Scenario 3 — Marcar notificação como lida

- **GIVEN** que a notificação pertence ao cliente autenticado
- **WHEN** o cliente envia `PATCH /notifications/:id` com `{ read_at: "2024-01-01T12:00:00Z" }`
- **THEN** o sistema **MUST** atualizar `read_at` da notificação, retornar `200 OK`

### Scenario 4 — Notificação pertence a outro usuário

- **GIVEN** que o `notification_id` pertence a outro usuário
- **WHEN** o cliente tenta marcar como lida
- **THEN** o sistema **MUST** retornar `403 Forbidden`

### Scenario 5 — Redis indisponível para entrega WebSocket

- **GIVEN** que o Redis (usado pelo Socket.io adapter) está inacessível
- **WHEN** o sistema tenta publicar a notificação
- **THEN** a notificação **MUST** ser persistida no banco independentemente; a entrega em tempo real **MAY** ser degradada; o sistema **SHOULD** logar a falha de entrega em tempo real
