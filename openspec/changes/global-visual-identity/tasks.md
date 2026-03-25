## 1. Configuração de Base e Design Tokens

- [ ] 1.1 Configurar importação das fontes DM Sans e DM Mono no projeto Next.js.
- [ ] 1.2 Atualizar `tailwind.config.ts` com as novas cores (background, muted, primary) para os modos claro e escuro.
- [ ] 1.3 Adicionar variáveis CSS para as sombras neomórficas (`--sa`, `--sb`) no `globals.css`.
- [ ] 1.4 Criar utilitários CSS no Tailwind para as três elevações neomórficas: `elevated-lg`, `elevated-sm` e `inset-nm`.

## 2. Componentes Base Neomórficos (shadcn/ui)

- [ ] 2.1 Customizar componente `Button` para suportar estilos neomórficos elevados e o botão CTA Primário com brilho de acento.
- [ ] 2.2 Customizar componente `Input` para aplicar a sombra interna (`inset-nm`) e remover bordas.
- [ ] 2.3 Criar um wrapper `NeomorphicCard` com `border-radius: 22px` e sombra `elevated-lg`.
- [ ] 2.4 Implementar o componente `Badge` customizado para categorias.

## 3. Sistema Visual de Categorias

- [ ] 3.1 Criar mapeamento de cores estáticas para as 16 categorias de serviço.
- [ ] 3.2 Desenvolver helper para gerar cores translúcidas (`rgba(cor, 0.14)`) para fundos de ícones.
- [ ] 3.3 Garantir que os contadores de serviço dentro dos cards utilizem a fonte `DM Mono`.

## 4. Landing Page v2 - Estrutura e Hero

- [ ] 4.1 Criar o `Header` neomórfico fixo com logo e links de navegação.
- [ ] 4.2 Desenvolver a seção `Hero` com headline principal e subtítulo.
- [ ] 4.3 Implementar a Barra de Busca afundada com ícone de lupa.
- [ ] 4.4 Adicionar as Category Pills elevadas logo abaixo da barra de busca.

## 5. Landing Page v2 - Conteúdo e Seções

- [ ] 5.1 Implementar a seção de Diferenciais com os 3 cards neomórficos (IA, Match, LGPD).
- [ ] 5.2 Desenvolver o Grid 4x4 de categorias com os cards individuais.
- [ ] 5.3 Implementar o Footer com links e informações legais usando texto terciário.

## 6. Revisão e Testes Visuais

- [ ] 6.1 Validar o contraste de cores no Modo Claro (Lavanda Pó) para conformidade de acessibilidade.
- [ ] 6.2 Testar a responsividade das sombras neomórficas em diferentes tamanhos de tela.
- [ ] 6.3 Realizar auditoria visual para garantir que nenhuma borda sólida ou gradiente flat foi utilizado.
