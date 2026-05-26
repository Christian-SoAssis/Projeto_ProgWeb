## Why

Na Clean Architecture pura, Hooks React (camada visual / adaptadores de UI) e Casos de Uso (camada de aplicação pura) pertencem a círculos concêntricos diferentes. Misturar ou acoplar lógica de orquestração de aplicação (chamadas de API, gravação de storage, regras de negócio) dentro de hooks ou providers do React viola o Princípio da Responsabilidade Única (SRP) e a Regra de Dependência inegociável do Uncle Bob.
Esta alteração visa separar de forma absoluta qualquer lógica de aplicação remanescente dos hooks de apresentação, reduzindo-os a finos adaptadores visuais e mapeando toda a arquitetura em um arquivo `ARCHITECTURE.md` contendo um diagrama Mermaid detalhado de 4 círculos concêntricos e explicações conceituais robustas para a banca de avaliação acadêmica.

## What Changes

- **Auditoria arquitetural**: Mapeamento de todos os arquivos de `presentation/hooks/` e `presentation/providers/` para assegurar que não haja lógica de aplicação acoplada a eles.
- **Refatoração de Casos de Uso e Adaptadores**:
  - Garantir que `LoginUseCase`, `RegisterClientUseCase`, `RegisterProfessionalUseCase`, `LogoutUseCase` e `GetCurrentUserUseCase` retenham toda a lógica pura de aplicação de forma isolada do React/Next.js.
  - Reduzir o `AuthProvider` (`auth-provider.tsx`) a um fino adaptador de estado que apenas consome os casos de uso expostos pelo Composition Root (`container.ts`).
  - Reduzir `useAuth` hook a um acessor de contexto trivial (`useContext`), livre de qualquer lógica de aplicação.
- **Documentação de Arquitetura (`apps/web/ARCHITECTURE.md`)**:
  - Inserção de um diagrama de arquitetura Mermaid detalhado exibindo os 4 círculos concêntricos aninhados.
  - Tabela de mapeamento de pastas para círculos canônicos da Clean Architecture.
  - Dissertação explicativa sobre a distinção crucial entre Hooks e Casos de Uso e o travamento de regras via ESLint.

## Capabilities

### New Capabilities
- `clean-arch-enforcement`: Separação estrita entre adaptadores React (Hooks/Providers) e Casos de Uso Puros da Aplicação, com geração de documentação de arquitetura unificada e diagrama Mermaid aninhado.

## Impact

- **Código afetado**: `apps/web/src/presentation/providers/auth-provider.tsx`, `apps/web/src/presentation/hooks/use-auth.ts`.
- **Nova Documentação**: `apps/web/ARCHITECTURE.md` (criado).
- **Validação**: Build e typechecking do Next.js/TypeScript mantidos verdes e livres de erros.
