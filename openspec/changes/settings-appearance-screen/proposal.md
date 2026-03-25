## Why

A tela de "Aparência" é fundamental para a personalização da experiência do usuário no ServiçoJá. Dado que o design neomórfico se baseia fortemente na interação entre luz e sombra, oferecer um controle claro e tátil sobre o tema (Claro/Escuro) é crucial. Esta proposta visa criar um ambiente de configurações intuitivo, onde o usuário pode visualizar mudanças em tempo real e gerenciar suas preferências de sistema e notificações com clareza.

## What Changes

- **Interface de Configurações Neomórfica**: Organização da tela em seções (`Cards`) elevados que agrupam funcionalidades relacionadas.
- **Controle de Tema Avançado**:
    - `Segmented Control` neomórfico com um container afundado (*inset*) e uma opção ativa elevada que "sai" do fundo.
    - Card de `Live Preview` que mostra uma miniatura da interface reagindo à escolha do tema.
- **Sistema de Toggles e Navegação**:
    - Toggles neomórficos com trilha afundada e botão elevado deslizante (com brilho menta quando ativo).
    - Listas de configurações de conta com indicadores de navegação elevados.
- **Ação de Saída**: Botão `ghost` elevado para logout, utilizando a cor terracota (#b04020) para indicar uma ação destrutiva sem quebrar a estética neomórfica.

## Capabilities

### New Capabilities
- `theme-switcher-interface`: Componente de controle segmentado para alternância entre modo claro e escuro com preview dinâmico.
- `neomorphic-preference-toggles`: Sistema unificado de chaves liga/desliga seguindo os padrões de profundidade neomórficos.
- `settings-layout-system`: Estrutura de cards elevados e rows de configuração para uma navegação hierárquica em ajustes.

### Modified Capabilities
- `user-settings`: Expansão das capacidades de configuração do usuário para incluir personalização visual profunda e sincronização com o sistema.

## Impact

- **Frontend**: Gestão de estado global de tema; implementação de componentes de toggle e segmented control customizados; aplicação rigorosa dos tokens de Neomorfismo em estados ativos/inativos.
- **UX/UI**: Proporciona uma sensação de controle total sobre a interface, reforçando a identidade premium do aplicativo.
