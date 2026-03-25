## ADDED Requirements

### Requirement: neomorphic-chat-header
The chat MUST feature an elevated header with professional identity and real-time status.

#### Scenario: header-visuals
- **WHEN** the chat screen is rendered.
- **THEN** it must display:
  - Avatar: Circular neomorphic with category badge (e.g., hydraulics-blue).
  - Status: "Online" pulsating menta dot.
  - Controls: Info and call icons (elevated small) on the right.

### Requirement: active-contract-context-banner
An active contract summary must be permanently available at the top of the chat area.

#### Scenario: banner-content
- **WHEN** a service is in progress.
- **THEN** show a banner card:
  - Elevation: Elevated NM.
  - Accent: 3px top line in #1a9878 (Menta).
  - Details: "Contrato Ativo", "Em andamento", and "R$ 270,00" (DM Mono).
  - Actions: Small inset button "Ver contrato".
