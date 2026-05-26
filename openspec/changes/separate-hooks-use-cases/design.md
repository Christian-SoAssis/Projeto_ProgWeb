## Context

Atualmente, o frontend da aplicação (`apps/web`) foi refatorado para uma estrutura limpa de camadas. No entanto, para fins acadêmicos e defesa de banca, a separação conceitual entre o que é um Hook React (um adaptador de interface visual) e o que é um Caso de Uso (regra de aplicação pura, independente de framework) deve ser absolutamente evidente e sem sobreposições.
Esta alteração refina e audita o `AuthProvider` e o hook `useAuth` para garantir que nenhum deles contenha orquestração direta de lógica de aplicação, consolidando-os como meros tradutores do React para as use cases e gerando a documentação visual `ARCHITECTURE.md` para subsidiar a apresentação em banca.

## Goals / Non-Goals

**Goals:**
- **Auditoria de Hooks**: Assegurar que nenhum hook ou provider contenha código de regras de negócio, persistência de dados direta ou chamadas de API nativas.
- **Redução do Acessor `useAuth`**: Tornar o hook `useAuth` um acessor simples e direto de contexto, sem qualquer estado interno ou efeito paralelo (`useEffect`/`useState`) de lógica de negócios.
- **Documentação de Arquitetura (`ARCHITECTURE.md`)**: Gerar um diagrama de fluxo e camadas Mermaid de alta qualidade e uma explicação acadêmica rigorosa distinguindo Hooks e Casos de Uso.

**Non-Goals:**
- Alteração das APIs Rest do Backend.
- Modificação visual ou funcional das telas e componentes visuais do Next.js (shadcn/ui).

## Decisions

### 1. Separação Estrita de Círculos Concêntricos
Mapeamento arquitetural rigoroso dos arquivos:
- **Entities (Domínio)**: `src/domain/entities/`, `src/domain/value-objects/`, `src/domain/errors/`
- **Use Cases (Aplicação)**: `src/application/use-cases/`, `src/application/ports/`, `src/application/dto/`
- **Interface Adapters**: `src/infrastructure/repositories/`, `src/infrastructure/mappers/`, `src/presentation/providers/`, `src/presentation/hooks/`
- **Frameworks & Drivers**: `src/infrastructure/http/`, `src/infrastructure/storage/`, Roteadores e Componentes React/Next.js.

### 2. Acessor de Contexto Puro no Hook
O hook `use-auth.ts` será simplificado ao máximo:
```typescript
import { useContext } from "react";
import { AuthContext } from "../providers/auth-provider";

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth deve ser usado dentro de um AuthProvider");
  }
  return context;
};
```
Isso garante que toda a manipulação de estados do React fique contida estritamente no `AuthProvider` (que serve como Interface Adapter do React Context) e que as regras de aplicação em si residam de forma pura nos Use Cases correspondentes.

### 3. Estruturação do Diagrama Mermaid e Tabela no ARCHITECTURE.md
O arquivo `ARCHITECTURE.md` conterá um diagrama de fluxo com os subgraphs aninhados do Mermaid representando os 4 círculos concêntricos de Uncle Bob.

## Risks / Trade-offs

- **[Risco] Overhead de Classes nos Use Cases** → *Mitigação*: A clareza conceitual proporcionada pela separação estrita é de extrema importância para a banca examinadora acadêmica. O pequeno boilerplate adicional é justificado pelo ganho pedagógico e de design de software.
