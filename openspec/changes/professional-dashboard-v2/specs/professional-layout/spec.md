## ADDED Requirements

### Requirement: professional-sidebar-layout
The dashboard MUST feature a permanent 240px sidebar for navigation and branding.

#### Scenario: sidebar-navigation
- **WHEN** the dashboard is rendered on desktop.
- **THEN** it displays:
  - Sidebar: Elevated Large, 240px Width.
  - Active Item: "Dashboard" with Inset Shadow and Menta Text.
  - Profile Footer: Neomorphic circular avatar and "Online" menta dot.

### Requirement: executive-dashboard-greeting
The main content area must start with a high-level executive summary.

#### Scenario: greeting-header
- **WHEN** the page loads.
- **THEN** it displays:
  - Heading: "Painel Executivo" (Primary Text).
  - Subheading: Secondary text summary of the current day/status.
