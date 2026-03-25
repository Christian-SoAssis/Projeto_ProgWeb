## Why

O "Dashboard do Cliente" é o ponto de partida para os usuários acompanharem seus pedidos e interagirem com profissionais no ServiçoJá. Uma interface **mobile-first** com design neomórfico puro garante uma experiência tátil e premium, essencial para a retenção de usuários. A clareza no status dos pedidos e o acesso rápido a estatísticas e atividades recentes facilitam o gerenciamento dos serviços contratados.

## What Changes

- **Interface Mobile-First**: Otimização completa para telas de até 480px, seguindo os padrões de usabilidade em dispositivos móveis.
- **Header e Navegação Neomórfica**:
    - Header elevado com saudação personalizada e notificações.
    - Sistema de `Nav Pills` horizontais com scroll lateral, utilizando estados *inset* para a aba ativa.
- **Gestão de Pedidos e Atividades**:
    - Cards de pedidos elevados com indicadores de cor por categoria e status (Aberto, Em Andamento, Concluído).
    - Lista de atividades recentes com ícones neomórficos elevados.
    - Mini-cards de estatísticas rápidas (pedidos abertos, gastos, avaliação).

## Capabilities

### New Capabilities
- `mobile-client-dashboard-shell`: Estrutura base mobile com header elevado e navegação por pills.
- `order-status-tracking-view`: Listagem de cards de pedidos com lógica de cores de categoria e status dinâmico.
- `client-activity-widgets`: Lista de atividades recentes e row de mini-cards de estatísticas (Stats Rápido).

### Modified Capabilities
- `client-dashboard`: Atualização da funcionalidade de dashboard cliente para o novo padrão visual neomórfico e mobile-first.

## Impact

- **Frontend**: Desenvolvimento de componentes responsivos específicos para mobile; uso intensivo de Tailwind para layout de pills e listas; aplicação rigorosa dos tokens de Neomorfismo.
- **UX/UI**: Melhoria drástica na experiência do usuário em dispositivos móveis, reforçando a marca como moderna e eficiente.
