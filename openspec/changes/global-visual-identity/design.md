## Context

O ServiçoJá passará por uma reformulação visual completa para adotar a filosofia de **Neomorphism**. Diferente do design flat ou material, o neomorfismo simula elementos moldados a partir da mesma superfície, usando luz e sombra para criar profundidade. Esta mudança impactará o sistema de cores, tipografia, bordas e sombras de todos os componentes da plataforma.

## Goals / Non-Goals

**Goals:**
- Implementar o sistema de sombras duplas (clara no topo-esquerdo, escura no fundo-direito).
- Padronizar as variantes de cor "Lavanda" para os modos Claro e Escuro.
- Definir uma escala tipográfica usando DM Sans e DM Mono.
- Criar um mapeamento de cores estáticas para as 16 categorias de serviço.
- Assegurar que os inputs e campos de formulário usem sombras internas (*inset*).

**Non-Goals:**
- Uso de Glassmorphism ou gradientes decorativos.
- Alteração da lógica de backend ou regras de negócio (foco exclusivo na UI/UX).
- Suporte a outras fontes que não sejam DM Sans/Mono.

## Decisions

### 1. Sistema Neomórfico (Sombras)
A profundidade será controlada por variáveis de sombra baseadas na cor de fundo (`--bg`):
- **Elevado (Cards):** `-6px -6px 14px var(--sb), 6px 6px 14px var(--sa)`
- **Pequeno (Botões):** `-3px -3px 8px var(--sb), 3px 3px 8px var(--sa)`
- **Afundado (Inputs):** `inset -3px -3px 7px var(--sb), inset 3px 3px 7px var(--sa)`

### 2. Paleta de Cores
- **Modo Claro (Padrão):** Fundo `#d0ccdc`, Sombra Escura `#aca8b8`, Sombra Clara `#f4f0ff`. Acento `#1a9878`.
- **Modo Escuro:** Fundo `#252030`, Sombra Escura `#181422`, Sombra Clara `#322c3e`. Acento `#30c898`.

### 3. Tipografia
Importação via Google Fonts:
- **DM Sans**: Pesos 300, 400, 500, 600 para textos gerais.
- **DM Mono**: Para números, métricas e dados técnicos.

### 4. Componentes Base (shadcn/ui)
- Os componentes serão customizados para remover `border-width` e aplicar as `box-shadow` neomórficas.
- Botões CTA (Primários) usarão o Acento Primário com sombra de brilho (`box-shadow: 0 0 0 2px [brilho], 3px 3px 10px rgba(0,0,0,.25)`).

## Risks / Trade-offs

- **Acessibilidade**: Contrastes sutis do neomorfismo podem dificultar a visão para alguns usuários. Mitigaremos isso garantindo que os textos primários mantenham alto contraste (ex: `#140e20` sobre `#d0ccdc`).
- **Performance**: O uso intensivo de múltiplas sombras em grids grandes pode impactar o render em dispositivos de baixo desempenho.
- **Complexidade de CSS**: Manter a consistência das sombras em diferentes níveis de elevação exige rigor na aplicação das classes utilitárias.
