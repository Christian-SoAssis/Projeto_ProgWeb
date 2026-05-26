## Why

O frontend da aplicação atualmente utiliza uma arquitetura híbrida ou "clean-ish" onde lógica de domínio (tipos e dados), infraestrutura (chamadas diretas com `fetch` e manipulação de cookies/localStorage) e lógica de visualização (UI do React/Next.js) estão misturadas em `src/lib/api.ts` e `src/context/auth-context.tsx`. Essa mistura dificulta a testabilidade unitária isolada da lógica de negócios, viola a Regra de Dependência (Dependency Rule) do Uncle Bob e cria acoplamento direto com o framework React/Next.js e APIs do browser.
Para garantir a modularidade e uma arquitetura robusta que será apresentada em banca acadêmica, é imperativo migrar essa estrutura para a **Clean Architecture pura**, com 4 camadas concêntricas perfeitamente isoladas, Regra de Dependência travada por linting e o bug do registro de profissionais (que não persistia os tokens na sessão) formalmente corrigido.

## What Changes

A migração será executada de forma incremental seguindo as 4 camadas do Clean Architecture (Uncle Bob):

- **domain/**:
  - Criação de entidades puras (`UserEntity`, `ProfessionalEntity`, `CategoryEntity`) isoladas de frameworks.
  - Implementação de Value Objects para validação robusta (`EmailVo`, `CpfVo`, `AuthTokensVo`).
  - Criação de erros de domínio customizados (`DomainError`, `InvalidCredentialsError`).
- **application/**:
  - Definição de portas/interfaces de entrada e saída (`AuthRepositoryPort`, `TokenStoragePort`, `ProfessionalRepositoryPort`).
  - Criação de Data Transfer Objects (DTOs) estritamente tipados (`LoginDto`, `RegisterClientDto`, `RegisterProfessionalDto`).
  - Implementação dos Casos de Uso (`LoginUseCase`, `RegisterClientUseCase`, `RegisterProfessionalUseCase`, `LogoutUseCase`, `GetCurrentUserUseCase`).
  - Correção formal do comportamento de `RegisterProfessionalUseCase` para auto-autenticação ou persistência de tokens apropriada.
- **infrastructure/**:
  - Criação de cliente HTTP genérico baseado em fetch (`HttpClient`, substituindo `apiFetch`).
  - Repositórios concretos (`HttpAuthRepository`, `HttpProfessionalRepository`) e armazenamento de tokens em local storage (`LocalTokenStorage`).
  - Mappers estritos para conversão de DTOs da API em Entidades de Domínio (`UserMapper`).
- **presentation/**:
  - Reescrever o `AuthProvider` (`auth-provider.tsx`) e `useAuth` hook para depender unicamente dos Casos de Uso através de injeção de dependência e Composition Root (`container.ts`).
  - Excluir permanentemente os arquivos legados `src/lib/api.ts` e `src/context/auth-context.tsx`.
- **enforcement**:
  - Configuração do plugin `eslint-plugin-boundaries` ou regras estritas no ESLint para bloquear e lançar erro de build se a Regra de Dependência for violada.

## Capabilities

### New Capabilities
- `auth-clean-architecture`: Implementação de fluxos de autenticação, registro de cliente e profissional, obtenção de perfil logado e alternância de papéis estruturados sob Clean Architecture pura no frontend com isolamento estrito de portas e adaptadores.

### Modified Capabilities
<!-- No modified capabilities because there are no existing specification files or requirements changing in the main openspec specs directory -->

## Impact

- **Código Afetado**: `apps/web/src/context/auth-context.tsx` (removido), `apps/web/src/lib/api.ts` (removido).
- **Novos Módulos**: `apps/web/src/domain/`, `apps/web/src/application/`, `apps/web/src/infrastructure/`, `apps/web/src/presentation/`.
- **Configurações**: `apps/web/.eslintrc.json` ou `apps/web/package.json` para adicionar as regras do ESLint Boundaries.
- **Build / Lint**: `npm run build` e typechecking serão validados a cada etapa incremental para garantir estabilidade contínua.
