## ADDED Requirements

### Requirement: search-bar-inset
The left panel MUST feature a search bar that visually appears sunken into the background.

#### Scenario: search-input-visuals
- **WHEN** the search bar is rendered.
- **THEN** it must have:
  - Shadow: `inset -3px -3px 7px var(--sb), inset 3px 3px 7px var(--sa)`
  - Background: `--bg`
  - Icon: Lupa (Magnifying glass)
  - Text: "Encanadores em Varginha" (placeholder or current query)

### Requirement: horizontal-filter-pills
Filters must be presented as a scrollable horizontal list of neomorphic pills.

#### Scenario: filter-pill-states
- **WHEN** a filter (e.g., "Verificado", "Até R$100/h") is selected.
- **THEN** it transitions from an elevated state (`elevated-sm`) to an inset state (`inset-nm`) and changes text color to `#1a9878`.

### Requirement: results-scrolling
The list of professional cards must be independently scrollable without moving the header or the map.

#### Scenario: scroll-behavior
- **WHEN** the user scrolls the results.
- **THEN** only the left list panel scrolls vertically.
