## ADDED Requirements

### Requirement: header-neomorphic-fixed
The landing page MUST have a fixed header that uses neomorphic elevation to appear separated from the main content.

#### Scenario: header-visuals
- **WHEN** the user scrolls the page.
- **THEN** the header remains at the top with:
  - Background: `--bg`
  - Shadow: Elevated Small (sb/sa)
  - Logo: "ServiçoJá ⚡" with the bolt (⚡) in #1a9878.
  - Buttons: "Entrar" (ghost elevado) and "Cadastrar" (CTA #1a9878).

### Requirement: hero-section-v2
The hero section must provide a prominent search interface and quick access to categories.

#### Scenario: hero-content
- **WHEN** the page loads.
- **THEN** it displays:
  - Headline: "Encontre profissionais verificados perto de você" (Bold, Primary Text).
  - Search Bar: Inset (afundada) shadow, placeholder "Que serviço você precisa?".
  - Category Pills: Elevated Small, for 🔨 Hidráulica, ⚡ Elétrica, 🧹 Limpeza, ➕ Ver todas.

### Requirement: value-proposition-cards
The page must showcase service differentiators using neomorphic cards.

#### Scenario: value-cards-grid
- **WHEN** the user scrolls to the differentials section.
- **THEN** it displays 3 elevated cards:
  - "IA analisa sua foto"
  - "Match em 80ms"
  - "LGPD Certificado"
  - Icons for each must be in #1a9878 (menta).

### Requirement: categories-grid-v2
A 4x4 grid of all major service categories with specific visual indicators.

#### Scenario: individual-category-card
- **WHEN** viewing the category grid.
- **THEN** each card displays:
  - Icon with background tint (rgba(cor,.14)).
  - Category name.
  - Service count in DM Mono (#1a9878).
