## 1. Etapa 1: Camada de Domínio (domain/)

- [ ] 1.1 Criar entidade de usuário em `apps/web/src/domain/entities/user.entity.ts`
- [ ] 1.2 Criar entidade de profissional em `apps/web/src/domain/entities/professional.entity.ts`
- [ ] 1.3 Criar entidade de categoria em `apps/web/src/domain/entities/category.entity.ts`
- [ ] 1.4 Criar value objects em `apps/web/src/domain/value-objects/email.vo.ts`, `cpf.vo.ts` e `auth-tokens.vo.ts`
- [ ] 1.5 Criar erros customizados de domínio em `apps/web/src/domain/errors/domain.error.ts` e `invalid-credentials.error.ts`
- [ ] 1.6 Validar isolamento absoluto da camada domain/ (zero dependências de framework/Next.js/browser)

## 2. Etapa 2: Portas de Abstração e DTOs (application/ports + application/dto)

- [ ] 2.1 Criar porta do repositório de autenticação em `apps/web/src/application/ports/auth-repository.port.ts`
- [ ] 2.2 Criar porta do armazenamento de tokens em `apps/web/src/application/ports/token-storage.port.ts`
- [ ] 2.3 Criar porta do repositório de profissionais em `apps/web/src/application/ports/professional-repository.port.ts`
- [ ] 2.4 Criar DTOs de autenticação em `apps/web/src/application/dto/login.dto.ts`
- [ ] 2.5 Criar DTOs de cadastro de cliente em `apps/web/src/application/dto/register-client.dto.ts`
- [ ] 2.6 Criar DTOs de cadastro de profissional em `apps/web/src/application/dto/register-professional.dto.ts`

## 3. Etapa 3: Casos de Uso (application/use-cases/)

- [ ] 3.1 Criar caso de uso de login em `apps/web/src/application/use-cases/auth/login.use-case.ts`
- [ ] 3.2 Criar caso de uso de cadastro de cliente em `apps/web/src/application/use-cases/auth/register-client.use-case.ts`
- [ ] 3.3 Criar caso de uso de cadastro de profissional em `apps/web/src/application/use-cases/auth/register-professional.use-case.ts`
- [ ] 3.4 Criar caso de uso de logout em `apps/web/src/application/use-cases/auth/logout.use-case.ts`
- [ ] 3.5 Criar caso de uso de obter usuário logado em `apps/web/src/application/use-cases/auth/get-current-user.use-case.ts`

## 4. Etapa 4: Camada de Infraestrutura (infrastructure/)

- [ ] 4.1 Criar cliente HTTP customizado em `apps/web/src/infrastructure/http/http-client.ts`, `api-config.ts` e `http.error.ts`
- [ ] 4.2 Criar repositório concreto de autenticação em `apps/web/src/infrastructure/repositories/http-auth.repository.ts`
- [ ] 4.3 Criar repositório concreto de profissional em `apps/web/src/infrastructure/repositories/http-professional.repository.ts`
- [ ] 4.4 Criar armazenamento de tokens concreto em `apps/web/src/infrastructure/storage/local-token-storage.ts`
- [ ] 4.5 Criar mapper de conversão de entidades em `apps/web/src/infrastructure/mappers/user.mapper.ts`

## 5. Etapa 5: Camada de Apresentação e Injeção de Dependências (presentation/)

- [ ] 5.1 Criar Composition Root (injeção e instanciação) em `apps/web/src/presentation/container.ts`
- [ ] 5.2 Reescrever provedor de contexto de autenticação em `apps/web/src/presentation/providers/auth-provider.tsx`
- [ ] 5.3 Criar custom hook de autenticação em `apps/web/src/presentation/hooks/use-auth.ts`

## 6. Etapa 6: Imposição de Arquitetura e Limpeza final (enforcement + limpeza)

- [ ] 6.1 Configurar regras de lint restritivas no ESLint (`import/no-restricted-paths` ou `eslint-plugin-boundaries`)
- [ ] 6.2 Remover arquivos legados antigos `src/lib/api.ts` e `src/context/auth-context.tsx`
- [ ] 6.3 Executar build completo e typechecking no frontend para atestar sucesso da refatoração
