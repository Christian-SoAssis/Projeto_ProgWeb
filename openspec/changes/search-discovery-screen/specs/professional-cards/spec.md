## ADDED Requirements

### Requirement: professional-card-neomorphic
Each search result MUST be displayed in a neomorphic card with category-specific accents.

#### Scenario: professional-card-visuals
- **WHEN** a professional card is rendered.
- **THEN** it must have:
  - Shadow: `elevated-lg` (shadows sb/sa)
  - Top Strip: 3px solid line in the category color (e.g., #2e7bc4 for Hidráulica).
  - Avatar: Elevated small shadow around the service emoji.
  - Category Badge: Pill with translucent background (rgba(cor, 0.14)).

### Requirement: performance-metrics-display
Key metrics (rating, jobs, response time) must use the DM Mono font for a technical look.

#### Scenario: card-stats-rendering
- **WHEN** displaying professional stats.
- **THEN** use `DM Mono`:
  - Rating: ★ 4.97 (Color: #d4a00a).
  - Jobs: ✓ 214 jobs.
  - Response: ⚡ 12 min (Color: #1a9878).

### Requirement: action-button-ghost
The "Ver perfil" action must use a ghost button style with elevation.

#### Scenario: profile-button-visuals
- **WHEN** the card is hovered or rendered.
- **THEN** the "Ver perfil" button appears as a ghost element with elevated small shadow when active.
