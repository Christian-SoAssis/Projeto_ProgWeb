## ADDED Requirements

### Requirement: neomorphic-theme-switcher
The appearance section MUST include a tactile segmented control for theme selection.

#### Scenario: theme-switcher-visuals
- **WHEN** the user opens the appearance settings.
- **THEN** show:
  - Track: Inset shadow with 14px radius.
  - Active Option: Elevated small button within the track.
  - Inactive Option: Flush with the track.
- **SCENARIO**: Selecting "Claro" highlights the option in menta with a weight of 600.

### Requirement: live-interface-preview
A real-time visual representation of the selected theme must be displayed.

#### Scenario: preview-card-content
- **WHEN** a theme is selected.
- **THEN** the preview card (Elevated Medium) displays:
  - A schematic UI with the corresponding background and shadow tokens.
  - Elements like a mini-header and mini-cards mimicking the app layout.

### Requirement: system-theme-sync-toggle
An option to synchronize the app theme with the device settings.

#### Scenario: sync-toggle-styling
- **WHEN** viewing the sync option.
- **THEN** show a neomorphic toggle:
  - Track: Inset 13px radius.
  - Dot: Elevated, sliding to the right with a menta glow when "On".
