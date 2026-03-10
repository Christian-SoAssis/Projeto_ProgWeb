# Spec: service-request

## ADDED Requirements

### Requirement: Criação de pedido de serviço
O sistema SHALL permitir ao cliente criar um pedido com título, descrição, categoria, localização, urgência, orçamento e fotos opcionais.

#### Scenario: Pedido criado com sucesso
- **WHEN** cliente autenticado envia POST /requests com dados válidos
- **THEN** sistema cria pedido com status='open', retorna 201 com id e campos ai_* como null (análise assíncrona)

#### Scenario: Pedido sem localização
- **WHEN** cliente omite campo de localização
- **THEN** sistema retorna 422 com erro no campo location

---

### Requirement: Upload de imagens no pedido
O sistema SHALL aceitar até 5 imagens por pedido, armazenadas no S3/MinIO.

#### Scenario: Upload bem-sucedido
- **WHEN** cliente envia imagens válidas (jpg/png, max 10MB cada) junto ao pedido
- **THEN** sistema armazena no S3, cria registros em request_images com analyzed=false, enfileira análise VLM

#### Scenario: Imagem com tamanho excedido
- **WHEN** cliente envia imagem > 10MB
- **THEN** sistema retorna 413 com mensagem de limite de tamanho

---

### Requirement: Análise assíncrona de imagem por VLM
O sistema SHALL processar imagens assincronamente via Gemini Vision API para classificar complexidade, urgência e especialidades.

#### Scenario: Análise VLM bem-sucedida
- **WHEN** worker BullMQ processa imagem na fila
- **THEN** sistema chama Gemini Vision, salva output JSON em campos ai_complexity, ai_urgency, ai_specialties do request

#### Scenario: Falha na API VLM
- **WHEN** Gemini Vision retorna erro ou timeout > 10s
- **THEN** worker retenta até 3× com backoff exponencial; após 3 falhas, campos ai_* permanecem null e matching usa apenas features tradicionais

---

### Requirement: Listagem de pedidos do cliente
O sistema SHALL retornar todos os pedidos do cliente autenticado com paginação.

#### Scenario: Listagem de pedidos ativos
- **WHEN** cliente autenticado envia GET /requests?status=open
- **THEN** sistema retorna lista paginada de pedidos com status 'open' do cliente

#### Scenario: Pedido não encontrado
- **WHEN** cliente tenta acessar GET /requests/:id de outro cliente
- **THEN** sistema retorna 403 Forbidden

---

### Requirement: Categorias de serviço
O sistema SHALL manter hierarquia de categorias navegável.

#### Scenario: Listagem de categorias raiz
- **WHEN** qualquer usuário envia GET /categories
- **THEN** sistema retorna categorias de nível raiz com contagem de subcategorias

#### Scenario: Listagem de subcategorias
- **WHEN** usuário envia GET /categories/:id/children
- **THEN** sistema retorna subcategorias da categoria especificada
