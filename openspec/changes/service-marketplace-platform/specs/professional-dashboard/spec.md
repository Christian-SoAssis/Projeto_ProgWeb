# Spec: professional-dashboard

## ADDED Requirements

### Requirement: Visualização de agenda e bids pendentes
O sistema SHALL exibir ao profissional seus bids pendentes e agenda de contratos ativos.

#### Scenario: Bids pendentes do profissional
- **WHEN** profissional autenticado acessa GET /professionals/me/bids?status=pending
- **THEN** sistema retorna lista de bids pendentes com detalhes do pedido e cliente

#### Scenario: Agenda de contratos ativos
- **WHEN** profissional acessa GET /professionals/me/contracts?status=active
- **THEN** sistema retorna contratos ativos com dados do cliente, valor e status

---

### Requirement: Métricas de performance do profissional
O sistema SHALL exibir métricas de earnings, taxa de conversão e reputation_score.

#### Scenario: Métricas do painel
- **WHEN** profissional acessa GET /professionals/me/metrics
- **THEN** sistema retorna: total_earned_cents, conversion_rate, avg_rating, completed_jobs, reputation_score, scores por dimensão

---

### Requirement: Atualização de perfil do profissional
O sistema SHALL permitir ao profissional atualizar bio, localização, raio de atendimento e tarifa.

#### Scenario: Atualização bem-sucedida
- **WHEN** profissional envia PATCH /professionals/me com campos válidos
- **THEN** sistema atualiza os campos e retorna perfil atualizado; se localização mudou, regenera embedding e re-indexa no Typesense

---

### Requirement: Histórico de earnings
O sistema SHALL exibir histórico de pagamentos recebidos com filtro por período.

#### Scenario: Histórico filtrado por mês
- **WHEN** profissional envia GET /professionals/me/earnings?from=2024-01&to=2024-03
- **THEN** sistema retorna lista de pagamentos no período com totais
