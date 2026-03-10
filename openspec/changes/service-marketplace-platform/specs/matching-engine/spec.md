# Spec: matching-engine

## ADDED Requirements

### Requirement: Endpoint de matching de profissionais
O sistema SHALL retornar lista rankeada de profissionais compatíveis com um pedido em < 80ms.

#### Scenario: Matching com dados completos
- **WHEN** cliente autenticado envia GET /requests/:id/matches
- **THEN** sistema retorna top-10 profissionais rankeados com score e features principais, em < 80ms

#### Scenario: Pedido sem imagens analisadas
- **WHEN** campos ai_* do request são null
- **THEN** sistema usa matching baseado em regras (geo + categoria + reputação) sem penalidade

#### Scenario: Nenhum profissional disponível
- **WHEN** nenhum profissional atende geo-radius + categoria
- **THEN** sistema retorna lista vazia com sugestão de ampliar raio ou categoria

---

### Requirement: Matching v0 por regras (cold-start)
O sistema SHALL usar matching baseado em regras enquanto não há dados suficientes para LTR.

#### Scenario: Matching por regras
- **WHEN** base de contratos < 500 registros
- **THEN** sistema usa filtros: geo-radius < 20km, match de categoria, ordenação por reputation_score desc

---

### Requirement: Microservice Python LTR
O sistema SHALL expor endpoint de scoring LightGBM via FastAPI Python.

#### Scenario: Scoring LTR bem-sucedido
- **WHEN** BFF envia POST /score com lista de features por profissional
- **THEN** microservice retorna scores rankeados em < 50ms para lote de até 50 candidatos

#### Scenario: Microservice indisponível
- **WHEN** microservice Python não responde em 3s
- **THEN** BFF faz fallback para matching v0 por regras e loga o evento

---

### Requirement: Feedback Loop de Treinamento
O sistema SHALL logar impressões e contratações para re-treinamento semanal do modelo LTR.

#### Scenario: Log de impressão
- **WHEN** matching retorna lista de profissionais para cliente
- **THEN** sistema registra evento de impressão (request_id, professional_id, position, features)

#### Scenario: Log de conversão
- **WHEN** cliente aceita bid de um profissional
- **THEN** sistema registra evento de conversão (label positiva para o profissional contratado)
