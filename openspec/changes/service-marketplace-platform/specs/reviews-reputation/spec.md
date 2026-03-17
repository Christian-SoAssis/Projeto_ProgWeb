# Spec: reviews-reputation

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Submissão de avaliação pós-serviço

O sistema **SHALL** permitir ao cliente avaliar o profissional apenas após a conclusão do contrato com pagamento confirmado. Avaliações duplicadas **MUST NOT** ser aceitas.

### Scenario 1 — Review submetida com sucesso

- **GIVEN** que o contrato tem `status='completed'`, pertence ao cliente autenticado e nenhuma review existe para o mesmo `contract_id`
- **WHEN** o cliente envia `POST /reviews` com `{ contract_id, rating: 4, text: "..." }`
- **THEN** o sistema **MUST** criar a review, enfileirar análise NLP no BullMQ, retornar `201 Created` com `id` da review; os campos `score_*` **MUST** ser `null` inicialmente

### Scenario 2 — Contrato não concluído

- **GIVEN** que o contrato tem `status != 'completed'`
- **WHEN** o cliente tenta submeter review
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com mensagem `"Contrato não finalizado — pagamento pendente"`

### Scenario 3 — Review duplicada

- **GIVEN** que já existe review para o mesmo `contract_id`
- **WHEN** o cliente tenta submeter nova review
- **THEN** o sistema **MUST** retornar `409 Conflict`

### Scenario 4 — Rating fora do intervalo válido

- **GIVEN** que o campo `rating` é menor que 1 ou maior que 5
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe no campo `rating` (validação Pydantic v2)

### Scenario 5 — PostgreSQL indisponível

- **GIVEN** que o banco está inacessível
- **WHEN** o sistema tenta persistir a review
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`; **MUST NOT** enfileirar análise NLP sem garantia de que a review foi salva

### Scenario 6 — Validação de front-end falha (campo `text` muito curto)

- **GIVEN** que o front-end envia `text` com menos de 10 caracteres (abaixo do mínimo definido)
- **WHEN** a requisição é validada pelo schema Pydantic v2 do FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe no campo `text`; a UI **SHOULD** ter validação inline para evitar requisições desnecessárias ao backend

---

## Requirement: Análise NLP de reviews por dimensão

O sistema **SHALL** analisar o texto da review com BERTimbau para extrair scores por dimensão: pontualidade, qualidade técnica, limpeza, comunicação.

### Scenario 1 — Análise NLP bem-sucedida

- **GIVEN** que o job de análise está na fila BullMQ e o BERTimbau API está disponível
- **WHEN** o worker processa o job
- **THEN** o sistema **MUST** atualizar `score_punctuality`, `score_quality`, `score_cleanliness`, `score_communication` na review; **MUST** disparar recálculo do `reputation_score` do profissional

### Scenario 2 — BERTimbau indisponível — fallback para Gemini

- **GIVEN** que a API BERTimbau retorna erro HTTP 5xx ou timeout > 5 s
- **WHEN** o worker tenta a análise principal
- **THEN** o worker **MUST** tentar análise via Gemini API como fallback; se bem-sucedido, **MUST** atualizar scores normalmente; **MUST** logar que o fallback foi usado

### Scenario 3 — BERTimbau e Gemini ambos indisponíveis

- **GIVEN** que ambas as APIs falham após retry
- **WHEN** o worker exaure as tentativas
- **THEN** os campos `score_*` **MUST** permanecer `null`; a review **MUST** aparecer no perfil com nota numérica (1–5) mas sem gráfico de dimensões; o evento **MUST** ser logado para reprocessamento posterior

---

## Requirement: Detecção de reviews inautênticas

O sistema **SHALL** detectar reviews suspeitas (fake, spam, burst temporal) e removê-las do cálculo de reputação.

### Scenario 1 — Review classificada como autêntica

- **GIVEN** que a análise NLP não detecta padrões suspeitos
- **WHEN** o worker conclui a classificação
- **THEN** `is_authentic=true`; a review **MUST** ser exibida no perfil e **MUST** ser contabilizada no `reputation_score`

### Scenario 2 — Review suspeita detectada

- **GIVEN** que a análise detecta padrões como: similaridade de texto > 90% com outra review, texto genérico demais, ou burst de reviews do mesmo usuário em < 1 h
- **WHEN** o worker classifica a review
- **THEN** `is_authentic=false`; a review **MUST NOT** ser contabilizada no `reputation_score`; **MUST** ser marcada para revisão manual no painel admin; a UI **MUST** ocultar a review até decisão do admin

---

## Requirement: Recálculo de reputação do profissional

O sistema **SHALL** recalcular o `reputation_score` do profissional após cada nova review autêntica processada.

### Scenario 1 — Recálculo bem-sucedido

- **GIVEN** que uma nova review autêntica teve seus `score_*` preenchidos pela análise NLP
- **WHEN** o worker finaliza a análise
- **THEN** o sistema **MUST** recalcular: `score = 0.3×avg(quality) + 0.25×avg(punctuality) + 0.2×avg(communication) + 0.15×avg(cleanliness) + 0.1×(completed_jobs_factor)`; **MUST** atualizar `professionals.reputation_score` dentro de transação atômica

### Scenario 2 — Falha no recálculo (transação revertida)

- **GIVEN** que a transação de atualização do `reputation_score` falha (ex.: lock timeout)
- **WHEN** o banco efetua rollback
- **THEN** o worker **MUST** retentar em até 3× com backoff; **MUST** logar a falha; scores anteriores **MUST** ser preservados

---

## Requirement: Exibição de reputação granular no perfil

O sistema **SHALL** exibir scores por dimensão apenas quando o profissional possui dados suficientes para uma representação estatisticamente confiável.

### Scenario 1 — Perfil com reviews suficientes (≥ 3 autênticas)

- **GIVEN** que o profissional possui ao menos 3 reviews com `is_authentic=true` e `score_* != null`
- **WHEN** qualquer usuário acessa `GET /professionals/:id`
- **THEN** a resposta **MUST** incluir objeto `reputation_dimensions: { punctuality, quality, cleanliness, communication }` com valores float

### Scenario 2 — Perfil sem reviews suficientes

- **GIVEN** que o profissional possui menos de 3 reviews autênticas
- **WHEN** o perfil é acessado
- **THEN** a resposta **MUST** retornar `reputation_dimensions: null`; a UI **MUST** exibir mensagem `"Reputação em construção"` no lugar do gráfico radar

### Scenario 3 — Profissional não encontrado

- **GIVEN** que o `professional_id` não existe no banco
- **WHEN** `GET /professionals/:id` é chamado
- **THEN** o sistema **MUST** retornar `404 Not Found`
