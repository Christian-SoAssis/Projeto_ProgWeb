## ADDED Requirements

### Requirement: mobile-neomorphic-header
The dashboard MUST feature an elevated header specifically designed for mobile viewports.

#### Scenario: header-content
- **WHEN** the dashboard is viewed on mobile (max-width 480px).
- **THEN** show:
  - Welcome Text: "Olá, João!" (Primary Text).
  - Notification Badge: Elevated Small with a numeric counter.

### Requirement: horizontal-scroll-nav-pills
Navigation between dashboard sections must be done via a horizontal scrollable list of neomorphic pills.

#### Scenario: nav-pill-styling
- **WHEN** a navigation pill is rendered.
- **THEN** it must have:
  - Border-radius: 50px.
  - Active State: Inset shadow (`inset-nm`) with menta text color.
  - Inactive State: Elevated small shadow (`elevated-sm`).
- **SCENARIO**: The list allows horizontal scrolling if pills exceed screen width.
