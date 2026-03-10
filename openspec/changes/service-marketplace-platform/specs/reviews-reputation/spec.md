# Spec: reviews-reputation

## ADDED Requirements

### Requirement: Submissão de avaliação pós-serviço
O sistema SHALL permitir ao cliente avaliar o profissional após conclusão do contrato com pagamento confirmado.

#### Scenario: Review submetida com sucesso
- **WHEN** cliente autenticado envia POST /reviews com contract_id, rating (1-5) e texto
- **THEN** sistema cria review, enfileira análise NLP, retorna 201

#### Scenario: Tentativa de review sem pagamento confirmado
- **WHEN** cliente tenta submeter review com contrato não concluído
- **THEN** sistema retorna 422 com mensagem "contrato não finalizado"

#### Scenario: Review duplicada
- **WHEN** cliente tenta submeter segunda review para o mesmo contrato
- **THEN** sistema retorna 409 Conflict

---

### Requirement: Análise NLP de reviews por dimensão
O sistema SHALL analisar o texto da review com BERTimbau para extrair scores por dimensão.

#### Scenario: Análise NLP bem-sucedida
- **WHEN** worker processa review na fila
- **THEN** sistema atualiza scores: score_punctuality, score_quality, score_cleanliness, score_communication

#### Scenario: Fallback para Gemini quando BERTimbau indisponível
- **WHEN** BERTimbau API retorna erro
- **THEN** worker usa Gemini API como fallback para análise de sentimento

---

### Requirement: Detecção de reviews inautênticas
O sistema SHALL detectar reviews suspeitas (fake, extremamente curtas, padrão de spam).

#### Scenario: Review autêntica detectada
- **WHEN** análise NLP classifica review como genuína
- **THEN** is_authentic=true, review exibida normalmente no perfil

#### Scenario: Review suspeita detectada
- **WHEN** análise detecta padrões suspeitos (score similarity alto, texto genérico, burst temporal)
- **THEN** is_authentic=false, review marcada para revisão admin, não contabilizada no reputation_score

---

### Requirement: Recálculo de reputação do profissional
O sistema SHALL recalcular o reputation_score do profissional após cada nova review autêntica.

#### Scenario: Recálculo pós-review
- **WHEN** nova review autêntica é registrada para um profissional
- **THEN** sistema recalcula: score = 0.3*avg(quality) + 0.25*avg(punctuality) + 0.2*avg(communication) + 0.15*avg(cleanliness) + 0.1*(completed_jobs_factor)

---

### Requirement: Exibição de reputação granular no perfil
O sistema SHALL exibir scores por dimensão no perfil do profissional como gráfico radar.

#### Scenario: Perfil com reviews suficientes
- **WHEN** usuário acessa GET /professionals/:id
- **THEN** resposta inclui scores por dimensão (apenas se >= 3 reviews autênticas)

#### Scenario: Perfil sem reviews suficientes
- **WHEN** profissional tem < 3 reviews autênticas
- **THEN** resposta retorna scores como null, UI exibe "Reputação em construção"
