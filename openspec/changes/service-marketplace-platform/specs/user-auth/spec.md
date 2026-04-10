# Spec: user-auth

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Cadastro de cliente

O sistema **SHALL** permitir registro de clientes com nome, e-mail e senha (hash bcrypt). O e-mail **MUST** ser único no banco de dados.

### Scenario 1 — Cadastro bem-sucedido

- **GIVEN** que nenhum usuário com o mesmo e-mail existe no banco
- **WHEN** o cliente envia `POST /auth/register` com `{ name, email, password }` válidos
- **THEN** o sistema **MUST** criar o usuário com `role='client'`, retornar `201 Created` com `access_token` (exp: 15 min) e `refresh_token` (exp: 7 dias)

### Scenario 2 — Campo obrigatório ausente (validação Pydantic)

- **GIVEN** que o payload omite um campo obrigatório (ex.: `email`)
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com lista de erros por campo; **MUST NOT** persistir nada no banco

### Scenario 3 — E-mail duplicado

- **GIVEN** que já existe um usuário com o mesmo e-mail no PostgreSQL
- **WHEN** o cliente envia `POST /auth/register` com esse e-mail
- **THEN** o sistema **MUST** retornar `409 Conflict` com mensagem `"E-mail já cadastrado"`

### Scenario 4 — PostgreSQL indisponível

- **GIVEN** que o banco de dados PostgreSQL está inacessível (container down, timeout)
- **WHEN** a requisição de cadastro é recebida
- **THEN** o sistema **MUST** retornar `503 Service Unavailable` com mensagem genérica; **MUST NOT** expor detalhes internos de conexão

---

## Requirement: Login com e-mail e senha

O sistema **SHALL** autenticar usuários com e-mail e senha, retornando par JWT.

### Scenario 1 — Login bem-sucedido

- **GIVEN** que o usuário existe com credenciais válidas
- **WHEN** o cliente envia `POST /auth/login` com `{ email, password }` corretos
- **THEN** o sistema **MUST** retornar `200 OK` com `access_token` (exp: 15 min) e `refresh_token` (exp: 7 dias)

### Scenario 2 — Credenciais inválidas

- **GIVEN** que o e-mail existe mas a senha está incorreta
- **WHEN** o cliente envia `POST /auth/login`
- **THEN** o sistema **MUST** retornar `401 Unauthorized` com mensagem `"Credenciais inválidas"`; **MUST NOT** indicar se o e-mail ou a senha estão errados separadamente (prevenção de enumeração)

### Scenario 3 — Usuário não encontrado

- **GIVEN** que nenhum usuário com o e-mail informado existe
- **WHEN** o cliente envia `POST /auth/login`
- **THEN** o sistema **MUST** retornar `401 Unauthorized` (mesma mensagem genérica que o Scenario 2)

### Scenario 4 — PostgreSQL indisponível durante login

- **GIVEN** que o banco de dados está inacessível
- **WHEN** a requisição de login é recebida
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

---

## Requirement: OAuth2 Social Login (Google)

O sistema **SHALL** permitir login/cadastro via Google OAuth2.

### Scenario 1 — Primeiro acesso via Google

- **GIVEN** que não existe conta com o e-mail retornado pelo Google
- **WHEN** o usuário completa o fluxo OAuth2 com Google e o callback é recebido em `GET /auth/google/callback`
- **THEN** o sistema **MUST** criar conta com `role='client'`, retornar `200 OK` com par JWT

### Scenario 2 — Conta existente vinculada ao Google

- **GIVEN** que já existe usuário com o e-mail retornado pelo Google
- **WHEN** o callback OAuth2 é recebido
- **THEN** o sistema **MUST** vincular as contas e retornar par JWT sem criar duplicata

### Scenario 3 — Token Google inválido ou expirado

- **GIVEN** que o código de autorização Google é inválido ou expirado
- **WHEN** o sistema tenta trocar o código por token junto ao Google
- **THEN** o sistema **MUST** retornar `401 Unauthorized` com mensagem `"Falha na autenticação social"`

---

## Requirement: Refresh Token Rotation

O sistema **SHALL** manter sessões longas via refresh token com rotação automática. Tokens usados **MUST** ser invalidados imediatamente após uso.

### Scenario 1 — Renovação bem-sucedida

- **GIVEN** que o `refresh_token` enviado é válido e não foi revogado
- **WHEN** o cliente envia `POST /auth/refresh` com o token
- **THEN** o sistema **MUST** invalidar o token atual, emitir novo par `access_token` + `refresh_token` e retornar `200 OK`

### Scenario 2 — Refresh token expirado

- **GIVEN** que o `refresh_token` ultrapassou 7 dias
- **WHEN** o cliente envia `POST /auth/refresh`
- **THEN** o sistema **MUST** retornar `401 Unauthorized`; o cliente **MUST** refazer login completo

### Scenario 3 — Refresh token já utilizado (detecção de replay)

- **GIVEN** que o `refresh_token` já foi utilizado anteriormente (rotação)
- **WHEN** o cliente tenta reutilizá-lo
- **THEN** o sistema **MUST** retornar `401 Unauthorized` e **SHOULD** revogar toda a família de tokens do usuário como medida de segurança

---

## Requirement: Cadastro de profissional

O sistema **SHALL** permitir registro de profissionais com dados adicionais (bio, localização, especialidades, documentos).

### Scenario 1 — Cadastro com documentos válidos

- **GIVEN** que os dados do profissional são válidos e o documento (CPF/CNPJ) foi enviado
- **WHEN** o usuário envia `POST /professionals` com dados e arquivo de documento
- **THEN** o sistema **MUST** criar usuário com `role='professional'`, `is_verified=false`, armazenar documento no filesystem local via abstração `IStorage`, retornar `201 Created`

### Scenario 2 — Campo obrigatório ausente

- **GIVEN** que o payload omite campo obrigatório do schema Pydantic v2
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe do(s) campo(s) inválido(s)

### Scenario 3 — Falha no upload

- **GIVEN** que o diretório de uploads está indisponível (sem permissão de escrita ou disco cheio) ao tentar salvar o documento
- **WHEN** o cadastro de profissional é processado
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`; **MUST NOT** criar o registro de usuário parcial no banco (operação **MUST** ser atômica: ou tudo persiste ou nada)

### Scenario 4 — Documento com formato inválido

- **GIVEN** que o arquivo enviado não é PDF, JPG ou PNG
- **WHEN** o FastAPI valida o upload
- **THEN** o sistema **MUST** retornar `415 Unsupported Media Type`

---

## Requirement: Aprovação de profissional pelo admin

O sistema **SHALL** manter fluxo obrigatório de verificação manual de profissionais por um admin antes de poderem receber ou enviar bids.

### Scenario 1 — Admin aprova profissional

- **GIVEN** que o profissional está com `is_verified=false`
- **WHEN** admin autenticado envia `PATCH /admin/professionals/:id` com `{ status: 'verified' }`
- **THEN** o sistema **MUST** atualizar `is_verified=true`, atualizar `search_vector` (FTS) do profissional no PostgreSQL, enviar notificação ao profissional, retornar `200 OK`

### Scenario 2 — Admin rejeita profissional

- **GIVEN** que o profissional está pendente de verificação
- **WHEN** admin envia `PATCH /admin/professionals/:id` com `{ status: 'rejected', reason: '...' }`
- **THEN** o sistema **MUST** manter `is_verified=false`, notificar o profissional com o motivo da rejeição

### Scenario 3 — Usuário não-admin tenta aprovar

- **GIVEN** que o token JWT pertence a um usuário com `role != 'admin'`
- **WHEN** a requisição chega ao endpoint `/admin/*`
- **THEN** o sistema **MUST** retornar `403 Forbidden`
