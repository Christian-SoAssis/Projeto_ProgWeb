# Spec: matching-engine

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Endpoint de matching de profissionais

O sistema **SHALL** retornar lista rankeada de até 10 profissionais compatíveis com um pedido em menos de 80 ms (p95).

### Scenario 1 — Matching com dados completos (LTR ativo)

- **GIVEN** que o pedido existe, pertence ao cliente autenticado e o microservice LTR está acessível
- **WHEN** o cliente envia `GET /requests/:id/matches`
- **THEN** o sistema **MUST** executar o matching module internamente e retornar lista de até 10 profissionais rankeados com `score`, features principais e distância em km, em menos de 80 ms

### Scenario 2 — Pedido com campos `ai_*` ainda nulos (análise VLM pendente)

- **GIVEN** que os campos `ai_complexity`, `ai_urgency`, `ai_specialties` do request são `null`
- **WHEN** o matching é solicitado
- **THEN** o sistema **MUST** processar o matching sem penalidade usando apenas features tradicionais (geo + categoria + reputação); **MUST NOT** bloquear ou retornar erro

### Scenario 3 — Nenhum profissional disponível

- **GIVEN** que nenhum profissional atende ao filtro de raio geográfico + categoria
- **WHEN** o matching é executado
- **THEN** o sistema **MUST** retornar lista vazia `[]` e **SHOULD** incluir mensagem `"Nenhum profissional encontrado. Tente ampliar o raio ou mudar a categoria"`

### Scenario 4 — Pedido não pertence ao cliente

- **GIVEN** que o `request_id` existe mas pertence a outro cliente
- **WHEN** o cliente envia `GET /requests/:id/matches`
- **THEN** o sistema **MUST** retornar `403 Forbidden`

### Scenario 5 — Pedido inexistente

- **GIVEN** que o `request_id` não existe no banco
- **WHEN** a requisição é recebida
- **THEN** o sistema **MUST** retornar `404 Not Found`

### Scenario 6 — PostgreSQL indisponível durante matching

- **GIVEN** que o banco está inacessível ao buscar candidatos
- **WHEN** o sistema executa a query inicial de candidatos
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

---

## Requirement: Matching v0 por regras (cold-start)

O sistema **SHALL** usar matching baseado em regras enquanto o modelo LTR não possui dados suficientes (< 500 contratos históricos).

### Scenario 1 — Ativação do matching por regras

- **GIVEN** que a tabela `contracts` possui menos de 500 registros com label positiva
- **WHEN** o matching é solicitado
- **THEN** o sistema **MUST** usar filtros em sequência: `geo-radius ≤ 20 km` → `match de category_id` → `is_verified=true` → ordenação por `reputation_score DESC`

### Scenario 2 — Transição automática para LTR

- **GIVEN** que o número de contratos históricos ultrapassa 500
- **WHEN** o modelo LTR é re-treinado e publicado
- **THEN** o endpoint **MUST** começar a usar o microservice LTR sem necessidade de restart manual

---

## Requirement: Matching Engine (Módulo Python Interno)

O sistema **SHALL** expor interface de scoring LightGBM via módulo `app.matching` invocado assincronamente pelo BFF.

### Scenario 1 — Scoring LTR bem-sucedido
- **GIVEN** que o BFF invoca a função de scoring com features válidas
- **WHEN** o processamento é concluído
- **THEN** o módulo **MUST** retornar scores rankeados em menos de 50 ms; os dados **MUST** ser validados por Pydantic v2

### Scenario 2 — Falha na validação de features
- **GIVEN** que o BFF passa dados que violam o schema Pydantic v2 do módulo
- **WHEN** a função é invocada
- **THEN** o módulo **MUST** levantar `ValidationError`; o BFF **MUST** capturar a exceção e fazer fallback para matching v0 por regras

### Scenario 3 — Erro interno no processamento de ML
- **GIVEN** que o LightGBM falha (ex: modelo corrompido ou erro de memória)
- **WHEN** o scoring é executado
- **THEN** o sistema **MUST** capturar o erro, logar com nível `CRITICAL` e fazer fallback para matching v0 por regras; **MUST NOT** retornar erro 500 ao cliente

---

## Requirement: Feedback Loop de Treinamento

O sistema **SHALL** registrar impressões e conversões para re-treinamento semanal do modelo LTR.

### Scenario 1 — Log de impressão (exposição)

- **GIVEN** que o matching retornou lista de profissionais para um cliente
- **WHEN** a resposta é enviada ao cliente
- **THEN** o sistema **MUST** inserir evento `{ type: 'impression', request_id, professional_id, position, features, timestamp }` na tabela de eventos ou fila assíncrona; esta operação **MUST NOT** impactar a latência do endpoint de matching

### Scenario 2 — Log de conversão (contratação)

- **GIVEN** que o cliente aceitou o bid de um profissional
- **WHEN** o contrato é criado
- **THEN** o sistema **MUST** registrar evento `{ type: 'conversion', request_id, professional_id, bid_id }` como label positiva para o modelo

### Scenario 3 — Falha ao gravar evento de log

- **GIVEN** que a tabela/fila de logging de eventos está inacessível
- **WHEN** o sistema tenta registrar o evento
- **THEN** o sistema **MUST NOT** interromper o fluxo principal (matching ou aceitação de bid); o erro **SHOULD** ser logado assincronamente para monitoramento
