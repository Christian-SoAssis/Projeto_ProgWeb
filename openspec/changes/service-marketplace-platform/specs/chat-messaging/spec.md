# Spec: chat-messaging

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Chat in-app entre cliente e profissional

O sistema **SHALL** fornecer chat em tempo real via WebSocket entre cliente e profissional de um contrato ativo. Comunicação fora da plataforma **MUST NOT** ser incentivada.

### Scenario 1 — Conexão WebSocket estabelecida com sucesso

- **GIVEN** que o usuário (cliente ou profissional) está autenticado com JWT válido e pertence ao contrato
- **WHEN** conecta ao endpoint WebSocket `ws://host/contracts/:id/chat`
- **THEN** o sistema **MUST** aceitar a conexão, registrá-la no Redis adapter e confirmar conexão ao cliente

### Scenario 2 — Mensagem enviada e entregue com sucesso

- **GIVEN** que o usuário é participante do contrato (`client_id` ou `professional_id`) e a conexão WebSocket está ativa
- **WHEN** o usuário envia mensagem via WebSocket
- **THEN** o sistema **MUST** persistir a mensagem em `messages` com `sender_id` e `created_at`; **MUST** entregar ao destinatário em tempo real (< 500 ms se online); **MUST** enfileirar análise NLP de desintermediação de forma assíncrona

### Scenario 3 — JWT ausente ou inválido na conexão WebSocket

- **GIVEN** que o token JWT não está presente no handshake WebSocket ou expirou
- **WHEN** o servidor tenta validar a conexão
- **THEN** o sistema **MUST** recusar a conexão com código WebSocket `4001` (não autorizado); **MUST NOT** abrir o socket

### Scenario 4 — Usuário não pertence ao contrato

- **GIVEN** que o JWT é válido mas o `user_id` não corresponde a `client_id` nem `professional_id` do contrato
- **WHEN** o usuário tenta conectar ao chat do contrato
- **THEN** o sistema **MUST** fechar o socket com código `4003` (proibido)

### Scenario 5 — PostgreSQL indisponível durante persistência da mensagem

- **GIVEN** que o banco está inacessível ao tentar salvar a mensagem
- **WHEN** o sistema tenta persistir o registro
- **THEN** o sistema **MUST** notificar o remetente via WebSocket do erro de entrega; **MUST NOT** descartar a mensagem silenciosamente; **SHOULD** colocar a mensagem em fila de retry

### Scenario 6 — Destinatário offline

- **GIVEN** que o destinatário não possui conexão WebSocket ativa
- **WHEN** a mensagem é enviada
- **THEN** o sistema **MUST** persistir a mensagem no banco; **SHOULD** enviar notificação push PWA ao destinatário

---

## Requirement: Histórico de mensagens

O sistema **SHALL** retornar histórico paginado de mensagens de um contrato via cursor-based pagination.

### Scenario 1 — Histórico recuperado com sucesso

- **GIVEN** que o usuário autenticado pertence ao contrato
- **WHEN** envia `GET /contracts/:id/messages?cursor=<message_id>&limit=50`
- **THEN** o sistema **MUST** retornar até 50 mensagens anteriores ao cursor, ordenadas por `created_at DESC`

### Scenario 2 — Usuário não pertence ao contrato

- **GIVEN** que o `user_id` não faz parte do contrato especificado
- **WHEN** envia `GET /contracts/:id/messages`
- **THEN** o sistema **MUST** retornar `403 Forbidden`

### Scenario 3 — Contrato inexistente

- **GIVEN** que o `contract_id` não existe no banco
- **WHEN** a requisição é recebida
- **THEN** o sistema **MUST** retornar `404 Not Found`

### Scenario 4 — PostgreSQL indisponível durante busca de histórico

- **GIVEN** que o banco está inacessível
- **WHEN** a query de histórico é executada
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

---

## Requirement: Detecção de desintermediação via NLP

O sistema **SHALL** monitorar mensagens para detectar tentativas de contato externo à plataforma.

### Scenario 1 — Padrão de desintermediação detectado

- **GIVEN** que a mensagem foi persistida e enfileirada para análise NLP
- **WHEN** o worker analisa e detecta padrões suspeitos: número de telefone, "meu WhatsApp é", e-mail externo, "me chama no..."
- **THEN** o sistema **MUST** criar alerta em `flags` com `type='disintermediation'`, `contract_id` e `message_id`; **MUST** notificar o painel admin; **MUST NOT** bloquear nem deletar a mensagem automaticamente

### Scenario 2 — Mensagem sem padrão suspeito

- **GIVEN** que a análise NLP não detecta padrão de desintermediação
- **WHEN** o worker conclui a análise
- **THEN** nenhuma ação adicional é tomada; o processamento **MUST NOT** impactar a entrega da mensagem em tempo real

### Scenario 3 — Worker NLP indisponível

- **GIVEN** que o serviço de análise NLP está inacessível
- **WHEN** o job é processado
- **THEN** o worker **MUST** retentar até 3× com backoff exponencial; após falhas, **MUST** logar o evento; o fluxo de chat **MUST NOT** ser interrompido

---

## Requirement: Escalonamento horizontal via Redis pub/sub

O sistema **SHALL** suportar múltiplas instâncias do BFF sem perda de mensagens de WebSocket.

### Scenario 1 — Usuários em instâncias diferentes do BFF

- **GIVEN** que cliente e profissional estão conectados a instâncias diferentes do BFF (atrás de load balancer)
- **WHEN** o remetente envia mensagem
- **THEN** a mensagem **MUST** ser publicada no canal Redis do contrato; a instância do destinatário **MUST** recebê-la via Redis Subscriber e entregá-la ao WebSocket correto

### Scenario 2 — Redis indisponível

- **GIVEN** que o Redis está inacessível (container down)
- **WHEN** uma mensagem é enviada via WebSocket
- **THEN** o sistema **MUST** persistir a mensagem no banco; **MUST** notificar o remetente que a entrega em tempo real foi degradada; o sistema **SHOULD** tentar reconectar ao Redis com backoff
