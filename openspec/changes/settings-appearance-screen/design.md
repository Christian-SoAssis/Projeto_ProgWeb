## Context

A tela de "Configurações — Aparência" v2 é o centro de controle visual do ServiçoJá. Ela permite que os usuários personalizem a interface entre os modos Claro e Escuro, além de gerenciar notificações e ajustes de conta. O design utiliza componentes neomórficos de alta fidelidade para fornecer feedback tátil imediato sobre as escolhas do usuário.

## Goals / Non-Goals

**Goals:**
- Implementar o layout de configurações baseado em cards elevados.
- Desenvolver o `ThemeSegmentedControl` com estados internos e elevados.
- Criar o card de `LivePreview` reativo ao tema selecionado.
- Implementar o sistema de `NeomorphicToggle` para preferências do sistema e notificações.
- Integrar a seção de conta com links de navegação e ação de logout destrutiva.

**Non-Goals:**
- Implementação da lógica de persistência de tema no LocalStorage ou backend (foco na interface).
- Telas de edição de idioma ou região (serão links por enquanto).

## Decisions

### 1. Sistema de Controle de Tema
- **Segmented Control**: Container afundado (`inset`) com radius 14px. A opção ativa é um botão elevado (`elevated-sm`) com radius 10px, criando o efeito de uma peça que se destaca do trilho.
- **Live Preview**: Card elevado médio que renderiza uma miniatura simplificada da UI (header, cards, nav bar) refletindo o esquema de cores atual.

### 2. Seções e Preferências
- **Toggles Neomórficos**: Trilhas afundadas (`inset`) de 13px de radius. O botão deslizante é elevado e ganha brilho menta (#1a9878) quando na posição ativa.
- **Agrupamento**: Uso de cards elevados grandes (`elevated-lg`) para separar logicamente as seções de Aparência, Notificações e Conta.

### 3. Ações e Navegação de Conta
- **Rows de Conta**: Texto primário com indicador de navegação `›` em cinza elevado pequeno.
- **Sair da Conta**: Botão `ghost` elevado para manter a unidade visual, mas com texto em terracota (#b04020) para sinalizar perigo/saída.

## Risks / Trade-offs

- **Performance do Preview**: O card de preview deve ser leve (SVG ou CSS puro) para garantir que a alternância de tema seja instantânea.
- **Feedback Tátil**: O design neomórfico pode ser sutil demais para alguns usuários. Usaremos o brilho menta nos toggles ativos para reforçar o estado atual.
