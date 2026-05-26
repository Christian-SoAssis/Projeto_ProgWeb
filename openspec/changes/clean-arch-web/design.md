## Context

Atualmente, a lógica de autenticação do frontend (`apps/web`) reside no arquivo `src/context/auth-context.tsx`. Este arquivo acumula múltiplas responsabilidades:
1. Definição do estado global de autenticação (React Context).
2. Chamadas de rede diretas utilizando `apiFetch` (de `src/lib/api.ts`).
3. Interações com storage de persistência do browser (`localStorage` e `document.cookie`).
4. Fluxos de redirecionamento do roteador do Next.js (`useRouter`).
5. Definição inline da tipagem de `User`.

Essa sobreposição de responsabilidades viola o princípio da responsabilidade única e impede a testabilidade isolada. A adoção de Clean Architecture pura (Uncle Bob) resolve estes problemas ao segregar a aplicação em 4 camadas concêntricas e unidirecionais.

## Goals / Non-Goals

**Goals:**
- **Isolamento de Domínio (Entities)**: A camada `domain/` deve ser puramente TypeScript, sem qualquer importação de bibliotecas de terceiros, frameworks ou do Next.js.
- **Portas de Abstração (Ports)**: A camada `application/` deve orquestrar as regras de negócio de aplicação por meio de interfaces abstratas (Ports), garantindo injeção de dependência flexível.
- **Adaptação Limpa**: Implementações concretas de chamadas HTTP, localStorage, cookies e mappers devem residir em `infrastructure/`.
- **Composition Root**: Centralização da instanciação de classes e injeção de dependências no Composition Root (`presentation/container.ts`).
- **Resolução de Bug**: Resolver formalmente no caso de uso `RegisterProfessionalUseCase` o comportamento pós-cadastro profissional. O backend de registro `/professionals` não devolve tokens de sessão. O caso de uso deve encapsular o comportamento de sucesso de forma que o fluxo de UI decida/execute o redirecionamento adequado para `/login?registered=true`.
- **Lint de Fronteiras**: Configurar o ESLint (`eslint-plugin-boundaries` ou `import/no-restricted-paths`) para falhar builds se ocorrer violação das camadas concêntricas.

**Non-Goals:**
- Alteração das APIs Rest do Backend (todos os contratos existentes devem ser preservados).
- Refatoração dos componentes UI da aplicação (exceto onde for necessário reescrever o hook e provider de autenticação para conectar-se ao Composition Root).

## Decisions

### 1. Separação em 4 Círculos Concêntricos
As dependências devem obrigatoriamente fluir de fora para dentro:
`presentation ──► application ──► domain`
`infrastructure ──► application / domain`

### 2. Composition Root e Container de Injeção
Para evitar acoplamento direto da camada de apresentação (`presentation/`) com as implementações concretas de infraestrutura (`infrastructure/`), criaremos um arquivo `presentation/container.ts`. Este arquivo será o Composition Root, instanciando os repositórios reais e injetando-os nos casos de uso.
```typescript
// Exemplo conceitual do container.ts
const httpClient = new HttpClient(BASE_URL);
const tokenStorage = new LocalTokenStorage();
const authRepository = new HttpAuthRepository(httpClient);
const professionalRepository = new HttpProfessionalRepository(httpClient);

export const loginUseCase = new LoginUseCase(authRepository, tokenStorage);
export const registerClientUseCase = new RegisterClientUseCase(authRepository, tokenStorage);
export const registerProfessionalUseCase = new RegisterProfessionalUseCase(professionalRepository);
export const logoutUseCase = new LogoutUseCase(tokenStorage);
export const getCurrentUserUseCase = new GetCurrentUserUseCase(authRepository, tokenStorage);
```

### 3. Tratamento Estrito de Erros e Tipagem
- Erros de rede HTTP serão traduzidos pela camada de `infrastructure/repositories/` para erros de domínio correspondentes em `domain/errors/` (ex: `InvalidCredentialsError`, `DomainError`).
- A camada de apresentação tratará apenas erros de domínio herdados de `DomainError`.

### 4. Validação por Value Objects no Frontend
Implementação de regras de validação nos Value Objects:
- `EmailVo`: Encapsula a validação estrutural do endereço de e-mail.
- `CpfVo`: Encapsula a validação estrutural de CPF (11 dígitos, cálculos de dígitos verificadores).
- `AuthTokensVo`: Agrupa os tokens de acesso e refresh.

## Risks / Trade-offs

- **[Risco] Verbose / Overhead de Boilerplate** → *Mitigação*: A Clean Architecture de fato introduz mais classes e arquivos (Mappers, DTOs, Ports, Use Cases). O ganho na clareza para a banca acadêmica e a garantia de isolamento valem o boilerplate adicional.
- **[Risco] Roteamento de Next.js nos Use Cases** → *Mitigação*: Next.js (`useRouter`) pertence a frameworks/UI e não pode estar na camada de aplicação. Os casos de uso retornarão promessas resolvidas/rejeitadas, e a camada de apresentação (`presentation/providers/auth-provider.tsx` ou componentes) executará os redirecionamentos adequados baseados no resultado do caso de uso.
