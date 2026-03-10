# Spec: admin-dashboard

## ADDED Requirements

### Requirement: Aprovação e rejeição de profissionais
O sistema SHALL permitir ao admin visualizar profissionais pendentes e aprovar/rejeitar com justificativa.

#### Scenario: Listagem de profissionais pendentes
- **WHEN** admin autenticado acessa GET /admin/professionals?is_verified=false
- **THEN** sistema retorna lista de profissionais aguardando aprovação com documentos anexados

#### Scenario: Aprovação de profissional
- **WHEN** admin envia PATCH /admin/professionals/:id com status='verified'
- **THEN** sistema atualiza is_verified=true, notifica profissional

#### Scenario: Acesso não-admin
- **WHEN** usuário sem role='admin' tenta acessar rota /admin/*
- **THEN** sistema retorna 403 Forbidden

---

### Requirement: Monitoramento de flags de fraude
O sistema SHALL exibir ao admin alertas de desintermediação e reviews suspeitas.

#### Scenario: Visualização de alertas de desintermediação
- **WHEN** admin acessa GET /admin/flags?type=disintermediation
- **THEN** sistema retorna lista de mensagens flagadas com contrato e usuários envolvidos

#### Scenario: Visualização de reviews suspeitas
- **WHEN** admin acessa GET /admin/flags?type=fake_review
- **THEN** sistema retorna reviews com is_authentic=false para revisão manual

---

### Requirement: Dashboard de métricas gerais
O sistema SHALL exibir ao admin KPIs da plataforma.

#### Scenario: KPIs do painel admin
- **WHEN** admin acessa GET /admin/metrics
- **THEN** sistema retorna: MAU (Monthly Active Users), total de contratos no mês, GMV (Gross Merchandise Value), taxa de conversão de matches, latência média do matching
