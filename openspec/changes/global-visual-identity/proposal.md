## Why

A implementação de uma identidade visual premium e coesa é fundamental para posicionar o ServiçoJá como o principal marketplace de serviços locais no Brasil. O uso de **Neomorphism** puro proporciona uma interface moderna, orgânica e tátil, distinguindo a plataforma da concorrência e transmitindo confiança e sofisticação aos usuários.

A padronização global garante consistência entre todas as telas, facilitando a navegação e fortalecendo a marca, enquanto a introdução de um sistema de cores por categoria otimiza a descoberta de serviços.

## What Changes

- **Sistema de Design Neomórfico**: Implementação de regras globais de sombras duplas (clara/escura) para criar profundidade sem bordas visíveis.
- **Paleta de Cores "Lavanda"**: Introdução do modo claro padrão ("Lavanda Pó") e modo escuro alternativo ("Lavanda Noturna").
- **Tipografia Exclusiva**: Adoção das fontes DM Sans (interface) e DM Mono (dados), eliminando fontes padrão de sistema.
- **Categorização Visual**: Implementação de uma paleta de cores invariável para categorias de serviço (ex: hidráulica, elétrica, limpeza).
- **Landing Page Premium**: Criação de uma nova página inicial que exemplifica a aplicação total desta identidade visual no modo claro padrão.

## Capabilities

### New Capabilities
- `visual-identity-tokens`: Definição de todos os tokens de Tailwind e variáveis CSS para o sistema neomórfico e paletas de cores.
- `landing-page-v2`: Implementação da landing page com header neomórfico, seção Hero, grid de categorias e diferenciais.
- `category-visual-system`: Sistema de ícones e cores específicas para cada uma das 16 categorias de serviço.

### Modified Capabilities
- `theming-system`: Adaptação do sistema de troca de temas (Aparência) para suportar as novas variações de Lavanda.

## Impact

- **Frontend**: Atualização de `tailwind.config.ts`, `globals.css` e migração/criação de componentes baseados em `shadcn/ui` para o estilo neomórfico.
- **UX/UI**: Mudança significativa na percepção visual da plataforma, exigindo que novos componentes sigam rigorosamente a filosofia de sombras e profundidade definida.
