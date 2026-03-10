# Spec: chat-messaging

## ADDED Requirements

### Requirement: Chat in-app entre cliente e profissional
O sistema SHALL fornecer chat em tempo real via WebSocket entre cliente e profissional de um contrato ativo.

#### Scenario: Mensagem enviada com sucesso
- **WHEN** usuário autenticado (cliente ou profissional do contrato) envia mensagem via WebSocket
- **THEN** sistema persiste mensagem em messages, entrega ao destinatário em tempo real (< 500ms), retorna confirmação

#### Scenario: Usuário não pertence ao contrato
- **WHEN** usuário tenta enviar mensagem para chat de contrato que não é seu
- **THEN** sistema fecha o socket com código 403

---

### Requirement: Histórico de mensagens
O sistema SHALL retornar histórico paginado de mensagens de um contrato.

#### Scenario: Busca de histórico
- **WHEN** usuário autenticado do contrato envia GET /contracts/:id/messages?cursor=<id>
- **THEN** sistema retorna até 50 mensagens anteriores ao cursor, ordenadas por created_at desc

---

### Requirement: Detecção de desintermediação via NLP
O sistema SHALL monitorar mensagens para detectar tentativas de contato externo.

#### Scenario: Padrão de desintermediação detectado
- **WHEN** worker NLP analisa mensagem e detecta padrões como WhatsApp, número de telefone, e-mail externo
- **THEN** sistema emite alerta para painel admin com a mensagem suspeita e context do contrato

#### Scenario: Mensagem sem padrão suspeito
- **WHEN** worker NLP analisa mensagem e não detecta padrão suspeito
- **THEN** nenhuma ação adicional é tomada

---

### Requirement: Escalonamento horizontal via Redis pub/sub
O sistema SHALL suportar múltiplas instâncias do BFF sem perda de mensagens.

#### Scenario: Múltiplas instâncias do servidor
- **WHEN** cliente e profissional estão conectados a instâncias diferentes do BFF
- **THEN** mensagem é roteada via Redis pub/sub e entregue corretamente ao destinatário
