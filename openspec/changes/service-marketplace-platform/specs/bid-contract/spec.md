# Spec: bid-contract

## ADDED Requirements

### Requirement: Envio de orçamento pelo profissional
O sistema SHALL permitir ao profissional responder a pedidos abertos com uma proposta de bid.

#### Scenario: Bid enviado com sucesso
- **WHEN** profissional autenticado (is_verified=true) envia POST /bids com request_id, preço e mensagem
- **THEN** sistema cria bid com status='pending', notifica o cliente, retorna 201

#### Scenario: Profissional não verificado tenta enviar bid
- **WHEN** profissional com is_verified=false tenta enviar bid
- **THEN** sistema retorna 403 com mensagem "verificação pendente"

---

### Requirement: Aceitação ou rejeição de bid pelo cliente
O sistema SHALL permitir ao cliente aceitar ou rejeitar bids recebidos.

#### Scenario: Cliente aceita bid
- **WHEN** cliente autenticado envia PATCH /bids/:id com status='accepted'
- **THEN** sistema atualiza bid para accepted, cria contrato automaticamente, notifica profissional, retorna 200

#### Scenario: Cliente rejeita bid
- **WHEN** cliente envia PATCH /bids/:id com status='rejected'
- **THEN** sistema atualiza bid para rejected, notifica profissional, retorna 200

---

### Requirement: Criação automática de contrato
O sistema SHALL criar um contrato ao aceitar um bid.

#### Scenario: Contrato criado ao aceitar bid
- **WHEN** bid é aceito
- **THEN** sistema cria registro em contracts com status='active', agreed_cents=bid.price_cents, e atualiza request.status='matched'

---

### Requirement: Pagamento integrado via MercadoPago
O sistema SHALL processar pagamento ao concluir o serviço via MercadoPago com split-payment.

#### Scenario: Pagamento processado com sucesso
- **WHEN** cliente confirma conclusão do serviço e inicia pagamento
- **THEN** sistema cria cobrança no MercadoPago com split: (100-X)% ao profissional, X% à plataforma; webhook confirma pagamento

#### Scenario: Webhook de confirmação recebido
- **WHEN** MercadoPago envia webhook de pagamento aprovado
- **THEN** sistema atualiza contract.status='completed', libera saldo ao profissional, habilita fluxo de review

#### Scenario: Pagamento recusado
- **WHEN** pagamento é recusado
- **THEN** sistema mantém contract.status='active' e notifica cliente para tentar novamente

---

### Requirement: Disputa de contrato
O sistema SHALL suportar abertura de disputa em contratos via painel admin.

#### Scenario: Cliente abre disputa
- **WHEN** cliente envia POST /contracts/:id/dispute com motivo
- **THEN** sistema atualiza contract.status='disputed' e notifica admin
