# Spec: lgpd

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Exclusão de conta e anonimização de dados pessoais

O sistema **SHALL** permitir que qualquer usuário (cliente ou profissional) solicite a exclusão da própria conta. A exclusão **MUST** anonimizar todos os dados pessoais identificáveis, mantendo dados transacionais de forma desidentificada para fins contábeis e legais.

### Scenario 1 — Exclusão bem-sucedida (cliente)

- **GIVEN** que o usuário autenticado com `role='client'` deseja excluir sua conta
- **WHEN** envia `DELETE /auth/me` com senha de confirmação
- **THEN** o sistema **MUST**:
  - Anonimizar campos PII: `name → 'Usuário removido'`, `email → hash@anon.local`, `phone → null`, `cpf → null`
  - Manter registros de `contracts` e `reviews` com `user_id` referenciando o registro anonimizado
  - Remover documentos do S3/MinIO associados ao usuário
  - Revogar todos os tokens (access + refresh) ativos
  - Retornar `200 OK` com `{ message: "Conta excluída com sucesso" }`

### Scenario 2 — Exclusão bem-sucedida (profissional)

- **GIVEN** que o usuário autenticado com `role='professional'` deseja excluir sua conta
- **WHEN** envia `DELETE /auth/me` com senha de confirmação
- **THEN** o sistema **MUST** executar o mesmo fluxo do Scenario 1, e adicionalmente:
  - Remover perfil do índice Typesense
  - Cancelar bids pendentes (`status='cancelled'`)
  - Manter histórico de `contracts` completados de forma anonimizada

### Scenario 3 — Senha de confirmação incorreta

- **GIVEN** que o usuário envia `DELETE /auth/me` com senha incorreta
- **WHEN** o sistema valida a senha
- **THEN** **MUST** retornar `401 Unauthorized` com mensagem `"Senha incorreta"`; **MUST NOT** anonimizar nenhum dado

### Scenario 4 — Conta com contratos ativos em andamento

- **GIVEN** que o usuário possui contratos com `status='in_progress'`
- **WHEN** solicita exclusão via `DELETE /auth/me`
- **THEN** o sistema **MUST** retornar `409 Conflict` com mensagem `"Finalize ou cancele contratos ativos antes de excluir a conta"`

---

## Requirement: Log de consentimento no cadastro

O sistema **SHALL** registrar o consentimento explícito do usuário no momento do cadastro, armazenando evidência auditável conforme LGPD Art. 8.

### Scenario 1 — Registro com consentimento aceito

- **GIVEN** que o usuário está se cadastrando via `POST /auth/register` ou `POST /professionals`
- **WHEN** o payload inclui `{ consent_terms: true, consent_privacy: true }`
- **THEN** o sistema **MUST** criar registro na tabela `consent_logs` com: `user_id`, `consent_type` (terms/privacy), `accepted_at` (timestamp), `ip_address`, `user_agent`, `version` (versão dos termos aceitos)

### Scenario 2 — Registro sem consentimento

- **GIVEN** que o payload de cadastro omite `consent_terms` ou `consent_privacy`, ou envia `false`
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com mensagem `"Aceite dos termos de uso e política de privacidade é obrigatório"`; **MUST NOT** criar conta

### Scenario 3 — Consulta de consentimentos pelo usuário

- **GIVEN** que o usuário autenticado deseja visualizar seus consentimentos
- **WHEN** envia `GET /auth/me/consents`
- **THEN** o sistema **MUST** retornar lista de consentimentos com `consent_type`, `accepted_at` e `version`

---

## Requirement: Política de retenção de dados

O sistema **SHALL** definir prazos máximos de retenção por tipo de dado. Dados que excederem o prazo **MUST** ser anonimizados ou removidos por job automatizado.

### Prazos de retenção

| Tipo de dado | Prazo de retenção | Ação após expiração |
|---|---|---|
| Dados pessoais (PII) de contas inativas | 12 meses sem login | Anonimização automática |
| Logs de consentimento | 5 anos | Manutenção obrigatória (LGPD Art. 8 §2) |
| Contratos completados | 5 anos | Manutenção com PII anonimizado |
| Mensagens de chat | 24 meses | Remoção do conteúdo, manter metadata |
| Documentos de profissional (S3) | Até exclusão da conta ou 12 meses após inatividade | Remoção do arquivo |
| Logs de aplicação com PII | 90 dias | Remoção automática |

### Scenario 1 — Job de retenção processa conta inativa

- **GIVEN** que uma conta não realiza login há mais de 12 meses
- **WHEN** o job de retenção (cron diário) executa
- **THEN** o sistema **MUST** anonimizar PII da conta, enviar e-mail de notificação 30 dias antes da anonimização, manter registros transacionais desidentificados

### Scenario 2 — Dados dentro do prazo

- **GIVEN** que os dados de um usuário estão dentro do prazo de retenção
- **WHEN** o job de retenção executa
- **THEN** o sistema **MUST NOT** alterar nenhum dado do usuário

---

## Requirement: Mascaramento de CPF/documentos nos logs

O sistema **SHALL** mascarar todos os dados sensíveis (CPF, CNPJ, documentos, tokens) em logs de aplicação, impedindo exposição acidental em arquivos de log, stdout e sistemas de observabilidade.

### Scenario 1 — CPF mascarado em logs de request

- **GIVEN** que uma requisição contém CPF no body (ex.: cadastro de profissional)
- **WHEN** o middleware de logging registra a requisição
- **THEN** o sistema **MUST** mascarar o CPF no formato `***.***.***-XX` (últimos 2 dígitos visíveis) antes de gravar no log

### Scenario 2 — CNPJ mascarado em logs

- **GIVEN** que uma requisição contém CNPJ
- **WHEN** o middleware de logging registra a requisição
- **THEN** o sistema **MUST** mascarar no formato `**.***.****/****-XX`

### Scenario 3 — Documentos de upload não logados

- **GIVEN** que um upload de documento (PDF/JPG/PNG) é processado
- **WHEN** o sistema registra log da operação
- **THEN** o sistema **MUST** logar apenas o `file_id` e `content_type`; **MUST NOT** logar o conteúdo, nome original do arquivo ou path completo no S3

### Scenario 4 — Tokens JWT não logados em plaintext

- **GIVEN** que uma requisição autenticada é logada
- **WHEN** o middleware de logging registra headers
- **THEN** o sistema **MUST** substituir o header `Authorization` por `Bearer [REDACTED]` no log

### Scenario 5 — Dados sensíveis no OpenTelemetry

- **GIVEN** que traces e spans são enviados ao backend de observabilidade
- **WHEN** atributos de span contêm PII (CPF, e-mail, nome)
- **THEN** o sistema **MUST** aplicar o mesmo mascaramento antes de exportar o span; **SHOULD** usar um SpanProcessor customizado para sanitização
