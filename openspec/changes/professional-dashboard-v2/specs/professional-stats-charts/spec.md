## ADDED Requirements

### Requirement: neomorphic-stat-cards
The dashboard must include three elevated cards for the most important business metrics.

#### Scenario: stats-content
- **WHEN** displaying business stats.
- **THEN** show:
  - Ganhos: Value in DM Mono (e.g., R$ 4.280) with a "+12%" growth indicator in green.
  - Lances ativos: Count in DM Mono (e.g., 7) with a "+3 hoje" menta badge.
  - Reputação: Value in DM Mono (e.g., 4.97 ★) with an âmbar star.

### Requirement: inset-analytics-chart
A performance chart must be displayed within an inset (sunken) visual area.

#### Scenario: chart-visuals
- **WHEN** rendering the performance graph.
- **THEN** use:
  - Widget Container: Elevated Large.
  - Chart Plot Area: Inset Shadow (`inset-nm`) with background #dcd8e8.
  - Labels: DM Mono text.

### Requirement: granular-reputation-bars
Detailed reputation scores must be represented by neomorphic progress bars.

#### Scenario: reputation-bar-visuals
- **WHEN** viewing granular stats.
- **THEN** show 4 horizontal bars:
  - Track: Inset shadow.
  - Fill: #1a9878 (Menta).
  - Metrics: Displayed in DM Mono.
