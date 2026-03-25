## ADDED Requirements

### Requirement: neomorphic-stepper-navigation
The page MUST display a 3-step progress indicator at the top using neomorphic circles.

#### Scenario: stepper-step-2-active
- **WHEN** the user is on Step 2 ("Descreva").
- **THEN** the stepper shows:
  - Step 1: Filled #1a9878 with "✓".
  - Step 2: Inset shadow with a menta border.
  - Step 3: Elevated neutral circle with tertiary text.

### Requirement: description-form-card
The main interaction area must be a large neomorphic card containing media upload and text description.

#### Scenario: description-card-content
- **WHEN** the form is rendered.
- **THEN** it must include:
  - Headline: "Descreva o problema" (Primary Text).
  - Media Area: 200px Height, inset shadow, menta camera icon.
  - Text Area: 6-line height, inset shadow.
  - Metadata Fields: "Localização" and "Urgência" side-by-side with inset shadows.

### Requirement: call-to-action-button
The bottom of the page must feature a prominent CTA to proceed with the search.

#### Scenario: cta-visuals
- **WHEN** the user completes the description.
- **THEN** show a full-width button "Buscar profissionais →" in #1a9878 with elevated small shadow.
