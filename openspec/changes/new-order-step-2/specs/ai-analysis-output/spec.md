## ADDED Requirements

### Requirement: ai-analysis-result-panel
A secondary neomorphic card must display the AI's interpretation of the user's description.

#### Scenario: ai-panel-header
- **WHEN** the AI finishes analysis.
- **THEN** display a header with an elevated robot (🤖) icon and a "94% confiança" badge in menta.

### Requirement: ai-metric-bars
The panel must use progress bars to represent Complexity, Urgency, and Confidence levels.

#### Scenario: metric-bar-visuals
- **WHEN** displaying metrics.
- **THEN** use:
  - Tracks: Inset shadows (`inset-nm`).
  - Complexity Fill: 55% (Amarelo âmbar #d4a00a).
  - Urgency Fill: 85% (Terracota #b04020).
  - Confidence Fill: 94% (Menta #1a9878).
  - Values: Rendered in `DM Mono`.

### Requirement: ai-category-badges
The AI panel should confirm the detected categories using tinted neomorphic labels.

#### Scenario: category-badges
- **WHEN** categories are detected (e.g., Hidráulica).
- **THEN** show inset badges with category-specific backgrounds (e.g., rgba(#2e7bc4, 0.12)) and text colors.
