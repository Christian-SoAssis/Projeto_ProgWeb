## Why

O "Painel do Profissional" é a ferramenta central para os prestadores de serviço gerenciarem seus negócios no ServiçoJá. A transição para uma interface neomórfica de altíssimo nível (executive-grade) proporciona uma sensação de profissionalismo e clareza visual. Esta reformulação visa aumentar a produtividade dos profissionais, facilitando o acompanhamento de métricas críticas como ganhos, lances ativos e reputação granular.

## What Changes

- **Layout de Sidebar Executiva**: Implementação de uma barra lateral neomórfica elevada de 240px com navegação vertical e status de presença.
- **Ecossistema de Widgets Neomórficos**:
    - Stat Cards elevados com métricas em `DM Mono`.
    - Gráfico de linha interativo com área visual afundada (*inset*).
    - Barras de progresso neomórficas para reputação granular.
- **Gestão de Trabalhos Próximos**: Lista de agendamentos com indicadores de categoria por cores fixas.

## Capabilities

### New Capabilities
- `executive-sidebar-nav`: Sidebar fixa com logo, links de navegação neomórficos e perfil de rodapé.
- `analytics-dashboard-widgets`: Conjunto de cards de estatísticas (Ganhos, Lances, Reputação) e gráficos de desempenho.
- `job-scheduler-view`: Listagem de próximos trabalhos com faixas de cor por categoria e horários em `DM Mono`.

### Modified Capabilities
- `professional-dashboard`: Atualização da interface do painel existente para o novo padrão visual e de layout.

## Impact

- **Frontend**: Desenvolvimento de componentes de dashboard especializados; implementação de bibliotecas de gráficos (ex: Recharts ou Chart.js) com customização de estilo para o fundo `#dcd8e8`.
- **UX/UI**: Transformação da experiência do profissional em uma ferramenta de "gestão executiva".
