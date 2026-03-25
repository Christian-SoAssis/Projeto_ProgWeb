## Context

A tela de "Busca e Descoberta" utiliza um layout de **Split-Screen Desktop**. O painel esquerdo é focado em filtragem e listagem detalhada de profissionais, enquanto o painel direito fornece contexto geográfico via mapa vetorial. Toda a interface segue as diretrizes de neomorfismo (sombras duplas, sem bordas, cores Lavanda).

## Goals / Non-Goals

**Goals:**
- Implementar o layout 40/60 (Lista/Mapa).
- Criar a barra de busca afundada e pills de filtro interativas.
- Desenvolver o card de profissional com indicadores visuais de categoria e reputação.
- Integrar um mapa vetorial com estilo personalizado (#dcd8e8).

**Non-Goals:**
- Implementação de filtros complexos de backend (foco na UI/UX e estados de frontend).
- Navegação para telas de perfil (será tratado em outra proposta).

## Decisions

### 1. Layout Split-Screen
- **Painel Esquerdo (40%)**: `overflow-y: auto`, fundo `--bg` (#d0ccdc).
- **Painel Direito (60%)**: Posicionamento fixo/sticky para o mapa, fundo `#dcd8e8`.

### 2. Barra de Busca e Filtros
- **Busca**: Utiliza a classe `inset-nm`. Ícone de lupa à esquerda.
- **Filtros**: Lista horizontal de `Pills`.
    - Estado Inativo: Elevado pequeno (`elevated-sm`).
    - Estado Ativo: Afundado (`inset-nm`) com texto na cor do acento (#1a9878).

### 3. Professional Cards (Neomorphic)
- **Estrutura**: Elevação `elevated-lg` com `border-radius: 22px`.
- **Top Accent**: Uma borda superior de 3px usando a cor fixa da categoria do profissional.
- **Avatar**: `elevated-sm` com sombra e emoji.
- **Stats**: Uso de `DM Mono` para notas, contagem de jobs e tempo de resposta.

### 4. Estilo do Mapa
- Fundo base do mapa: `#dcd8e8`.
- Pins: Círculos com a cor da categoria. Pin selecionado com sombra de brilho menta.

## Risks / Trade-offs

- **Performance do Mapa**: Renderizar muitos pins simultaneamente pode afetar a fluidez. Usaremos agrupamento (*clustering*) se necessário.
- **Scrolling**: A sincronização entre a rolagem da lista e o foco no mapa requer gerenciamento cuidadoso de estado para evitar frustração do usuário.
