# Spec: user-auth

## ADDED Requirements

### Requirement: Cadastro de cliente
O sistema SHALL permitir registro de clientes com nome, e-mail e senha (hash bcrypt). E-mail deve ser único.

#### Scenario: Cadastro bem-sucedido
- **WHEN** usuário envia POST /auth/register com nome, e-mail e senha válidos
- **THEN** sistema cria o usuário com role='client', retorna 201 com JWT access_token e refresh_token

#### Scenario: E-mail duplicado
- **WHEN** usuário tenta cadastrar com e-mail já existente
- **THEN** sistema retorna 409 Conflict com mensagem de erro

---

### Requirement: Login com e-mail e senha
O sistema SHALL autenticar usuários com e-mail e senha, retornando JWT.

#### Scenario: Login bem-sucedido
- **WHEN** usuário envia POST /auth/login com credenciais válidas
- **THEN** sistema retorna 200 com access_token (exp: 15min) e refresh_token (exp: 7d)

#### Scenario: Credenciais inválidas
- **WHEN** usuário envia login com senha errada
- **THEN** sistema retorna 401 Unauthorized

---

### Requirement: OAuth2 Social Login (Google)
O sistema SHALL permitir login/cadastro via Google OAuth2.

#### Scenario: Primeiro acesso via Google
- **WHEN** usuário completa fluxo OAuth2 com Google
- **THEN** sistema cria conta com role='client' (se não existir) e retorna JWT

#### Scenario: Conta existente via Google
- **WHEN** usuário com e-mail já cadastrado faz login via Google
- **THEN** sistema vincula as contas e retorna JWT

---

### Requirement: Refresh Token Rotation
O sistema SHALL manter sessões via refresh token com rotação automática.

#### Scenario: Renovação de token
- **WHEN** cliente envia POST /auth/refresh com refresh_token válido
- **THEN** sistema invalida o token atual e retorna novo par access_token + refresh_token

#### Scenario: Refresh token expirado ou revogado
- **WHEN** cliente envia refresh_token inválido
- **THEN** sistema retorna 401 e força novo login

---

### Requirement: Cadastro de profissional
O sistema SHALL permitir registro de profissionais com dados adicionais (bio, localização, especialidades, documentos).

#### Scenario: Cadastro de profissional com documentos
- **WHEN** usuário envia POST /professionals com dados válidos incluindo upload de documento (CPF/CNPJ)
- **THEN** sistema cria usuário com role='professional', is_verified=false, armazena documento no S3, retorna 201

#### Scenario: Falta de documento obrigatório
- **WHEN** cadastro de profissional sem documento
- **THEN** sistema retorna 422 com detalhes do campo obrigatório

---

### Requirement: Aprovação de profissional pelo admin
O sistema SHALL manter fluxo de verificação manual de profissionais.

#### Scenario: Admin aprova profissional
- **WHEN** admin envia PATCH /admin/professionals/:id com status='verified'
- **THEN** sistema atualiza is_verified=true e envia notificação ao profissional

#### Scenario: Admin rejeita profissional
- **WHEN** admin envia PATCH /admin/professionals/:id com status='rejected' e motivo
- **THEN** sistema notifica o profissional com o motivo da rejeição
