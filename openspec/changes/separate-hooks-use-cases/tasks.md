## 1. Etapa 1: Auditoria Arquitetural (Auditar)

- [x] 1.1 Analisar e documentar toda a lógica de negócio ou orquestração remanescente no provedor e hooks
- [x] 1.2 Apresentar o relatório de auditoria detalhado

## 2. Etapa 2: Consolidação dos Casos de Uso (Mover a lógica)

- [x] 2.1 Garantir o isolamento total de `LoginUseCase` de qualquer dependência do React
- [x] 2.2 Garantir o isolamento total de `RegisterClientUseCase` de qualquer dependência do React
- [x] 2.3 Garantir o isolamento total de `RegisterProfessionalUseCase` de qualquer dependência do React
- [x] 2.4 Garantir o isolamento total de `LogoutUseCase` de qualquer dependência do React
- [x] 2.5 Garantir o isolamento total de `GetCurrentUserUseCase` de qualquer dependência do React

## 3. Etapa 3: Simplificação dos Hooks e Providers (Reduzir hooks)

- [x] 3.1 Refatorar `use-auth.ts` para ser um acessor trivial do React Context (`useContext`), sem lógica interna
- [x] 3.2 Refatorar `auth-provider.tsx` para atuar puramente como UI Interface Adapter (sem lógica de negócio ou orquestração própria)

## 4. Etapa 4: Validação e Compilação (Validar a separação)

- [x] 4.1 Executar a validação do linter ESLint para atestar conformidade das fronteiras arquiteturais
- [x] 4.2 Executar o typecheck focados para garantir compilação correta

## 5. Etapa 5: Geração da Documentação de Arquitetura (Gerar ARCHITECTURE.md)

- [x] 5.1 Criar `apps/web/ARCHITECTURE.md` contendo o diagrama Mermaid de 4 círculos aninhados
- [x] 5.2 Adicionar tabela de mapeamento de pastas a círculos canônicos
- [x] 5.3 Inserir explicação teórica detalhada (hook x caso de uso) no `ARCHITECTURE.md`
