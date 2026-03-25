## ADDED Requirements

### Requirement: neomorphic-notification-toggles
Notification preferences must be managed via a group of neomorphic toggles.

#### Scenario: notification-rows
- **WHEN** the notification section is rendered.
- **THEN** it displays 3 rows:
  - "Novos lances recebidos" (ON - menta glow).
  - "Mensagens no chat" (ON - menta glow).
  - "Atualizações de contrato" (OFF - gray elevated dot).
- **EVERY** row follows the inset track + elevated dot pattern.

### Requirement: account-navigation-rows
Account settings should be presented as navigable rows with elevated indicators.

#### Scenario: account-list-items
- **WHEN** viewing the account section.
- **THEN** show rows for "Idioma", "Região" and "Limpar cache".
- **EACH** row features an elevated small arrow indicator ("›") at the right.

### Requirement: destructive-logout-action
The logout action must be visually distinct while remaining neomorphic.

#### Scenario: logout-button-style
- **WHEN** the user scrolls to the bottom.
- **THEN** display a button:
  - Style: Ghost Elevated (no solid fill).
  - Text: Terracota (#b04020) with a logout icon.
  - Position: Centered bottom, 1.5rem margin-top.
