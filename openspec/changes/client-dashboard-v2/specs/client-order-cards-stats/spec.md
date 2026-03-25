## ADDED Requirements

### Requirement: active-order-cards
Ongoing service requests must be displayed as neomorphic cards with status and category indicators.

#### Scenario: order-card-layout
- **WHEN** an active order is listed.
- **THEN** show:
  - Card Shadow: Elevated Large.
  - Category Strip: 3px top line in category color.
  - Status Pill: Colored indicator (e.g., #2a8c50 for "Aberto").
  - Details Button: Ghost small button on the right.

### Requirement: client-stats-row
A summary of current activity should be displayed as a row of small elevated cards.

#### Scenario: quick-stats-content
- **WHEN** the dashboard loads.
- **THEN** display a row of 3 mini-cards:
  - Card 1: "3 abertos" 📋.
  - Card 2: "R$ 1.240" 💰.
  - Card 3: "4.9 ★" ⭐.
  - All values must use `DM Mono`.

### Requirement: recent-activity-list
A chronological list of recent platform events.

#### Scenario: activity-item-visuals
- **WHEN** an activity item is rendered.
- **THEN** it must have:
  - Icon: Neomorphic elevated emoji.
  - Description: Bold title + secondary detail.
  - Timestamp: DM Mono tertiary text.
