## ADDED Requirements

### Requirement: category-color-mapping
Each service category must have a unique, invariant color that is consistent across all themes.

#### Scenario: color-definitions
- **WHEN** rendering a category element.
- **THEN** use the Following colors:
  - Hidráulica: `#2e7bc4` (azul)
  - Elétrica: `#d4a00a` (amarelo âmbar)
  - Gás: `#e06820` (laranja)
  - Construção: `#b04020` (terracota)
  - Jardinagem: `#2a8c50` (verde folha)
  - Limpeza: `#18a0a0` (teal)
  - Pintura: `#9050c0` (roxo)
  - Marcenaria: `#8a5c28` (marrom madeira)
  - Ar-condicionado: `#4898d8` (azul gelo)
  - Segurança: `#384880` (azul marinho)
  - Tecnologia/TI: `#20a870` (verde esmeralda)
  - Reformas: `#c06840` (cobre)
  - Saúde e Beleza: `#d04080` (rosa)
  - Jurídico: `#485870` (cinza azulado)
  - Educação: `#e08820` (âmbar)
  - Pet: `#d85020` (laranja avermelhado)

### Requirement: category-icon-styling
Icons within category cards must follow a specific translucent tint style.

#### Scenario: icon-tint-rendering
- **WHEN** rendering a category icon.
- **THEN** it must have:
  - Background: `rgba(cor-da-categoria, 0.14)`
  - Text/Icon color: `cor-da-categoria`
  - Border (optional): `rgba(cor-da-categoria, 0.30)`
