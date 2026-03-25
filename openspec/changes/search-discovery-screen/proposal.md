## Why

A tela de "Busca e Descoberta" é o núcleo da experiência do usuário no ServiçoJá. Implementar esta tela com uma interface de split-screen premium e design neomórfico reforça a identidade visual da plataforma e oferece uma navegação intuitiva e moderna. A combinação de uma lista detalhada de profissionais com um mapa interativo facilita a tomada de decisão baseada em localização e reputação.

## What Changes

- **Layout Split-Screen**: Implementação de uma visualização dividida (40% lista / 60% mapa) otimizada para Desktop.
- **Painel de Resultados Neomórfico**:
    - Barra de busca com sombra interna (*inset*).
    - Filtros em pills neomórficas com feedback visual de estado ativo.
    - Cards de profissionais com elevação neomórfica e indicadores visuais por categoria.
- **Mapa Vetorial customizado**: Integração de um mapa com estilo visual coerente com a paleta Lavanda e pins dinâmicos.

## Capabilities

### New Capabilities
- `search-results-panel`: Implementação do painel esquerdo contendo a lógica de busca, filtros e listagem de cards.
- `discovery-map-view`: Implementação do painel direito com mapa vetorial, pins coloridos por categoria e popups neomórficos.
- `neomorphic-professional-card`: Componente de card especializado para exibir informações de profissionais (reputação, experiência, preço).

### Modified Capabilities
- `search-discovery`: Atualização dos requisitos de interface da capability de busca existente para suportar o novo layout e estilo.

## Impact

- **Frontend**: Criação de novos componentes de UI específicos para a busca; integração com bibliotecas de mapa (ex: Mapbox ou Leaflet) com customização de estilo.
- **UX/UI**: Transição de uma busca simples para uma experiência de "descoberta" mais rica e visual.
