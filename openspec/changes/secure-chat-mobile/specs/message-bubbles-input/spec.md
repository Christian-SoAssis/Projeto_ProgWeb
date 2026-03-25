## ADDED Requirements

### Requirement: neomorphic-bubbles-system
Messages must be represented by asymmetrical bubbles with different depth levels.

#### Scenario: message-styling
- **WHEN** a message is received (from professional).
- **THEN** it is:
  - Depth: Inset NM (sunken).
  - Shape: 4px top-left, 16px others.
  - Alignment: Left.
  - Background: #c4c0d0.
- **WHEN** a message is sent (from client).
- **THEN** it is:
  - Depth: Elevated Small.
  - Shape: 16px top-right, 4px others.
  - Alignment: Right.
  - Tint: rgba(26,152,120,.08).

### Requirement: neomorphic-input-bar
The text entry area must follow the inset neomorphic pattern.

#### Scenario: input-visuals
- **WHEN** the user is typing.
- **THEN** show:
  - Bar: Inset (50px border-radius).
  - Attachments: Camera and clip icons (elevated small) on the left.
  - Submit: Circular menta button (elevated) on the right.

### Requirement: chat-completion-action
A primary action button for service finalization must be fixed at the screen bottom.

#### Scenario: cta-behavior
- **WHEN** the contract is active.
- **THEN** display a fixed button:
  - Text: "Confirmar conclusão e avaliar →".
  - Elevation: Elevated Menta.
  - Radius: 14px.
