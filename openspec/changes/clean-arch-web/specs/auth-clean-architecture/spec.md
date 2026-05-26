## ADDED Requirements

### Requirement: Camada de Domínio Totalmente Isolada
A camada `domain/` SHALL ser autossuficiente e não conter dependências ou imports de frameworks (como React ou Next.js) ou do ambiente de execução do navegador (como fetch ou localStorage).

#### Scenario: Validação de Value Object de Email
- **WHEN** um email inválido for passado ao Value Object `EmailVo`
- **THEN** o construtor do `EmailVo` deve lançar um erro de domínio apropriado

#### Scenario: Entidade de Usuário Pura
- **WHEN** a entidade `UserEntity` for instanciada
- **THEN** ela não deve requerer nenhum tipo ou componente do React ou Next.js

### Requirement: Injeção de Dependências e Composition Root
A camada de apresentação (React components e providers) SHALL obter instâncias de casos de uso exclusivamente por meio de injeção de dependências proveniente do Composition Root (`presentation/container.ts`).

#### Scenario: Resolução de Casos de Uso
- **WHEN** o `AuthProvider` inicializar
- **THEN** ele deve resolver os casos de uso a partir do container unificado `presentation/container.ts`

### Requirement: Fluxo de Registro de Profissionais com Redirecionamento
O caso de uso de registro de profissional SHALL enviar os dados do profissional e reportar o resultado com sucesso, permitindo que a camada de apresentação execute o redirecionamento adequado para login já que o backend de registro não persiste tokens.

#### Scenario: Registro de Profissional sem Sessão Prévia
- **WHEN** o profissional for registrado com sucesso através do formulário
- **THEN** o sistema deve concluir a requisição no repositório de infraestrutura e redirecionar a UI para a tela de login `/login?registered=true`

### Requirement: Validação Automática de Regras de Dependência via ESLint
A arquitetura SHALL implementar regras automatizadas de lint para garantir que importações incorretas violando a Regra de Dependência quebrem o build.

#### Scenario: Importação Inválida da Infraestrutura pelo Domínio
- **WHEN** o desenvolvedor tentar importar qualquer arquivo de `infrastructure/` dentro de `domain/`
- **THEN** o ESLint deve gerar um erro de linting impedindo a compilação do projeto
