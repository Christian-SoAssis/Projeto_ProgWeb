## ADDED Requirements

### Requirement: core-neomorphic-tokens
The system must define a base background color and two auxiliary colors (one lighter, one darker) for each theme (Light and Dark) to achieve the neomorphic effect via double shadows.

#### Scenario: default-light-mode-tokens
- **WHEN** the application is in the default Light Mode ("Lavanda Pó").
- **THEN** the tokens must be:
  - `--bg`: `#d0ccdc`
  - `--sa` (shadow dark): `#aca8b8` (bg - ~13%)
  - `--sb` (shadow light): `#f4f0ff` (bg + ~12%)
  - Text Primary: `#140e20`
  - Text Secondary: `#584870`
  - Accent Primary: `#1a9878` (menta sóbria)

#### Scenario: alternating-dark-mode-tokens
- **WHEN** the application is switched to Dark Mode ("Lavanda Noturna").
- **THEN** the tokens must be:
  - `--bg`: `#252030`
  - `--sa` (shadow dark): `#181422` (bg - ~8%)
  - `--sb` (shadow light): `#322c3e` (bg + ~8%)
  - Text Primary: `#ddd8f0`
  - Text Secondary: `#8878b0`
  - Accent Primary: `#30c898` (menta vibrante)

### Requirement: neomorphic-shadow-rules
Components must follow specific shadow rules based on their type to maintain visual consistency.

#### Scenario: elevated-cards-shadows
- **WHEN** a component is a large container or card.
- **THEN** it must use `box-shadow: -6px -6px 14px var(--sb), 6px 6px 14px var(--sa)` and `border-radius: 22px`.

#### Scenario: inset-inputs-shadows
- **WHEN** a component is an input, search bar, or slider.
- **THEN** it must use `box-shadow: inset -3px -3px 7px var(--sb), inset 3px 3px 7px var(--sa)` and `border-radius: 12px-16px`.

### Requirement: typography-standardization
The interface must use fonts from the DM family, excluding any system or other common fonts.

#### Scenario: interface-font-dm-sans
- **WHEN** displaying standard text, labels, or UI elements.
- **THEN** use `DM Sans` with weights 300, 400, 500, 600.

#### Scenario: numeric-font-dm-mono
- **WHEN** displaying numerical data or metrics.
- **THEN** use `DM Mono`.
