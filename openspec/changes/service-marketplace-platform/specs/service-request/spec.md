# Spec: service-request

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Criação de pedido de serviço

O sistema **SHALL** permitir ao cliente criar um pedido com título, descrição, categoria, localização, urgência, orçamento e fotos opcionais.

### Scenario 1 — Pedido criado com sucesso

- **GIVEN** que o cliente está autenticado e todos os campos obrigatórios são fornecidos
- **WHEN** o cliente envia `POST /requests` com payload válido
- **THEN** o sistema **MUST** criar pedido com `status='open'`, retornar `201 Created` com `id` e campos `ai_*` como `null` (análise assíncrona); **MUST** enfileirar análise VLM se imagens foram enviadas

### Scenario 2 — Campo obrigatório ausente (validação Pydantic)

- **GIVEN** que o payload omite um campo obrigatório (ex.: `location`, `category_id`)
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com lista de erros por campo, sem persistir nada no banco

### Scenario 3 — Localização com coordenadas inválidas

- **GIVEN** que `latitude` está fora do intervalo `[-90, 90]` ou `longitude` fora de `[-180, 180]`
- **WHEN** a requisição é validada pelo schema Pydantic v2
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe do campo `location`

### Scenario 4 — PostgreSQL indisponível

- **GIVEN** que o banco de dados PostgreSQL está inacessível
- **WHEN** o sistema tenta persistir o pedido
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`; **MUST NOT** retornar stack trace ao cliente

### Scenario 5 — Cliente não autenticado

- **GIVEN** que o `Authorization` header está ausente ou o JWT é inválido/expirado
- **WHEN** a requisição chega ao endpoint `POST /requests`
- **THEN** o sistema **MUST** retornar `401 Unauthorized`

---

## Requirement: Upload de imagens no pedido

O sistema **SHALL** aceitar até 5 imagens por pedido (formatos: JPG, PNG), armazenadas no S3/MinIO.

### Scenario 1 — Upload bem-sucedido

- **GIVEN** que o cliente envia imagens válidas (JPG ou PNG, cada uma ≤ 10 MB) e não ultrapassou o limite de 5
- **WHEN** o upload é processado
- **THEN** o sistema **MUST** armazenar no S3/MinIO, criar registros em `request_images` com `analyzed=false`, enfileirar análise VLM no BullMQ, retornar `201 Created`

### Scenario 2 — Imagem com tamanho excedido

- **GIVEN** que ao menos uma imagem enviada excede 10 MB
- **WHEN** o sistema valida o upload
- **THEN** o sistema **MUST** retornar `413 Content Too Large` com mensagem `"Cada imagem deve ter no máximo 10 MB"`; **MUST NOT** armazenar nenhum arquivo do lote

### Scenario 3 — Formato de arquivo não suportado

- **GIVEN** que o cliente envia arquivo com extensão/MIME type diferente de `image/jpeg` ou `image/png`
- **WHEN** a validação é feita
- **THEN** o sistema **MUST** retornar `415 Unsupported Media Type`

### Scenario 4 — Limite de 5 imagens excedido

- **GIVEN** que o pedido já possui 5 imagens ou o cliente tenta enviar mais de 5 de uma vez
- **WHEN** o upload é recebido
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com mensagem `"Máximo de 5 imagens por pedido"`

### Scenario 5 — MinIO/S3 indisponível

- **GIVEN** que o serviço de armazenamento de objetos está inacessível
- **WHEN** o sistema tenta fazer upload
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`; o pedido base **MAY** ter sido criado; o cliente **SHOULD** ser orientado a tentar adicionar imagens novamente

---

## Requirement: Análise assíncrona de imagem por VLM

O sistema **SHALL** processar imagens assincronamente via Gemini Vision API para classificar complexidade, urgência e especialidades requeridas.

### Scenario 1 — Análise VLM bem-sucedida

- **GIVEN** que a imagem foi armazenada e o job está na fila BullMQ
- **WHEN** o worker processa o job Gemini Vision
- **THEN** o sistema **MUST** salvar `ai_complexity`, `ai_urgency`, `ai_specialties[]` no `request`; **MUST** atualizar `request_images.analyzed=true`

### Scenario 2 — Timeout ou erro da API Gemini Vision

- **GIVEN** que Gemini Vision não responde em 10 s ou retorna erro HTTP 5xx
- **WHEN** o worker tenta processar
- **THEN** o worker **MUST** retentar até 3× com backoff exponencial (ex.: 10s, 30s, 90s); após 3 falhas, os campos `ai_*` **MUST** permanecer `null` e o evento **MUST** ser logado; o matching **MUST** usar apenas features tradicionais como fallback

### Scenario 3 — Resposta da API fora do schema esperado

- **GIVEN** que a Gemini Vision retorna JSON com campos ausentes ou de tipo incorreto
- **WHEN** o worker tenta parsear o resultado com Pydantic v2
- **THEN** o worker **MUST** logar o erro de validação e tratar como falha (aplicar mesma lógica de retry do Scenario 2)

---

## Requirement: Listagem de pedidos do cliente

O sistema **SHALL** retornar todos os pedidos do cliente autenticado com paginação cursor-based.

### Scenario 1 — Listagem de pedidos ativos

- **GIVEN** que o cliente está autenticado
- **WHEN** envia `GET /requests?status=open` (ou `matched`, `in_progress`)
- **THEN** o sistema **MUST** retornar apenas os pedidos do próprio cliente com esse status; **MUST NOT** expor pedidos de outros clientes

### Scenario 2 — Acesso a pedido de outro cliente

- **GIVEN** que o `request_id` pertence a outro cliente
- **WHEN** o cliente envia `GET /requests/:id`
- **THEN** o sistema **MUST** retornar `403 Forbidden`

### Scenario 3 — Pedido inexistente

- **GIVEN** que o `request_id` não existe no banco
- **WHEN** o cliente envia `GET /requests/:id`
- **THEN** o sistema **MUST** retornar `404 Not Found`

### Scenario 4 — PostgreSQL indisponível durante listagem

- **GIVEN** que o banco está inacessível
- **WHEN** a query é executada
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

---

## Requirement: Categorias de serviço

O sistema **SHALL** manter hierarquia de categorias navegável, sem autenticação obrigatória.

### Scenario 1 — Listagem de categorias raiz

- **GIVEN** que nenhum filtro específico é aplicado
- **WHEN** qualquer usuário (autenticado ou não) envia `GET /categories`
- **THEN** o sistema **MUST** retornar categorias de nível raiz (`parent_id IS NULL`) com contagem de subcategorias; resposta **SHOULD** ser cacheada no Redis por 1 h

### Scenario 2 — Listagem de subcategorias

- **GIVEN** que o `category_id` fornecido existe e possui filhos
- **WHEN** o usuário envia `GET /categories/:id/children`
- **THEN** o sistema **MUST** retornar subcategorias diretas da categoria especificada

### Scenario 3 — Categoria inexistente

- **GIVEN** que o `category_id` não existe no banco
- **WHEN** o usuário envia `GET /categories/:id/children`
- **THEN** o sistema **MUST** retornar `404 Not Found`
