# Spec: client-dashboard

## ADDED Requirements

### Requirement: Visualização de pedidos ativos e histórico
O sistema SHALL exibir ao cliente seus pedidos em curso e histórico completo.

#### Scenario: Pedidos ativos
- **WHEN** cliente autenticado acessa GET /requests?status=open,matched,in_progress
- **THEN** sistema retorna pedidos ativos com status atual e bids recebidos

#### Scenario: Histórico de pedidos concluídos
- **WHEN** cliente acessa GET /requests?status=done&page=1
- **THEN** sistema retorna histórico paginado de pedidos finalizados

---

### Requirement: Lista de profissionais favoritos
O sistema SHALL permitir ao cliente salvar e visualizar profissionais favoritos.

#### Scenario: Adicionar favorito
- **WHEN** cliente envia POST /favorites com professional_id
- **THEN** sistema registra favorito e retorna 201

#### Scenario: Listar favoritos
- **WHEN** cliente acessa GET /favorites
- **THEN** sistema retorna lista de profissionais favoritados com scores de reputação

---

### Requirement: Notificações do cliente
O sistema SHALL entregar notificações em tempo real e push (PWA) sobre eventos relevantes.

#### Scenario: Notificação de bid recebido
- **WHEN** profissional envia bid para pedido do cliente
- **THEN** sistema cria notificação tipo='bid_received' e entrega via WebSocket se online, ou push PWA se offline

#### Scenario: Marcar notificação como lida
- **WHEN** cliente envia PATCH /notifications/:id com read_at
- **THEN** sistema atualiza notificação como lida
