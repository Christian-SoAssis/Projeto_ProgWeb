# Design System Document: The Tactile Interface

## 1. Overview & Creative North Star
**Creative North Star: "The Sculpted Surface"**

This design system moves away from the "sticker-on-glass" aesthetic of modern flat design and instead treats the user interface as a single, continuous physical substrate. For **ServiçoJá**, the goal is to evoke a sense of physical reliability and premium craftsmanship. 

By utilizing **Pure Neomorphism**, we transition from digital abstractions to "soft UI"—where every button, card, and input feels like it has been vacuum-formed or precision-milled from a single sheet of *Lavender Powder* (#d0ccdc). This is not just a layout; it is a landscape of light and shadow. We avoid all artificial borders and glass effects to maintain a "Mono-Material" philosophy that feels intentional, grounded, and bespoke.

---

## 2. Colors & Surface Philosophy
The palette is monochromatic and tonal, relying on the physics of light rather than hue to define boundaries.

### The Foundation
*   **Background (Surface):** `#d0ccdc` (Lavender Powder) - This is the "Base Plate" for the entire application.
*   **Accent (Action):** `#1a9878` (Mint) - Used sparingly for high-priority status indicators or primary action text.

### The "No-Line" Rule
Traditional 1px borders are strictly prohibited. In this system, a "line" is a failure of form. Separation is achieved through two methods:
1.  **Positive Elevation:** Light and Dark shadows creating a "raised" effect.
2.  **Negative Elevation (Inset):** Light and Dark shadows creating a "pressed" or "carved" effect.

### Surface Hierarchy
*   **Surface (Base):** `#d0ccdc`
*   **Surface Bright:** `#fcf8ff` (Used only for the lightest highlight of a shadow).
*   **Surface Dim:** `#dcd8e8` (Used for subtle background shifts in large sections).

---

## 3. Typography
We utilize a dual-font strategy to balance human-centric service with technical precision.

*   **Interface Elements (DM Sans):** Used for all headlines, buttons, and navigation. It provides a friendly, geometric clarity that complements the soft roundedness of the UI.
*   **Data & Counters (DM Mono):** Used for prices, timestamps, and service IDs. This creates a "machined" look, suggesting accuracy and professional auditing for the service marketplace.

### Typography Scale
*   **Display (Headline-LG):** 2rem / DM Sans Bold. Use for hero headers.
*   **Title (Title-MD):** 1.125rem / DM Sans Medium. Use for card titles.
*   **Data (Label-MD):** 0.75rem / DM Mono Regular. Use for pricing and metrics.

---

## 4. Elevation & Depth (The Neomorphic Engine)
Depth is the primary functional language of this system. All components must adhere to the following light-source logic (Light from Top-Left at 135°).

### The Layering Principle
*   **Elevated (Extruded):** For interactive elements like Buttons and Cards.
    *   *Light Shadow:* `-6px -6px 14px #f4f0ff`
    *   *Dark Shadow:* `6px 6px 14px #aca8b8`
*   **Inset (Concave):** For containers that hold data, like Search Bars and Form Fields.
    *   *Light Shadow (Inner):* `-6px -6px 14px #f4f0ff`
    *   *Dark Shadow (Inner):* `6px 6px 14px #aca8b8`

### Ambient Shadows
For "Floating" elements (like a Bottom Navigation bar), use a heightened elevation by doubling the blur (28px) and reducing the spread, ensuring the shadow color remains a tint of the background (`#aca8b8`) rather than a generic grey.

---

## 5. Components

### Buttons
*   **Primary Elevated:** Background `#d0ccdc`, elevated shadow. Text in `Primary (#006951)`.
*   **Active/Pressed:** Transition from Elevated to Inset shadow to provide tactile haptic feedback.
*   **Shape:** `Roundedness: lg (1rem)` to match the soft aesthetic.

### Input Fields & Search Bars
*   **Style:** Always **Inset**. The input should look like it was carved into the Lavender Powder surface.
*   **Typography:** `body-md` (DM Sans).
*   **Focus State:** No border. Increase the Dark Shadow intensity or add a subtle Mint (`#1a9878`) glow to the text cursor only.

### Cards
*   **Style:** Elevated surface. 
*   **Layout:** No divider lines. Use `Spacing: 4 (1.4rem)` to separate content blocks internally.
*   **Nesting:** If a card contains a list, the list items should be flat, separated by generous whitespace, or use very subtle "Ghost" Inset shadows.

### Chips (Service Categories)
*   **Unselected:** Elevated (appears "ready to be pressed").
*   **Selected:** Inset (appears "pushed in") with Mint (`#1a9878`) text.

---

## 6. Do's and Don'ts

### Do
*   **Use consistent light sources:** Ensure every shadow in the app follows the -6px/-6px and 6px/6px logic.
*   **Embrace negative space:** Since we don't use borders, whitespace is your only tool for grouping. Use the `Spacing Scale 6 (2rem)` for major sectioning.
*   **Soft Corners:** Always use `lg` (1rem) or `xl` (1.5rem) radiuses. Sharp corners break the neomorphic illusion.

### Don't
*   **No Glassmorphism:** Do not use `backdrop-blur` or transparency. The UI should look opaque and solid.
*   **No High Contrast Shadows:** Never use pure black (`#000000`) for shadows. Use the specified `Dark (#aca8b8)` value.
*   **No Gradients:** Avoid the temptation to add "shimmer" or "gloss." The "Pure" neomorphic style relies on the flat background color matching the surface perfectly.
*   **No Borders:** If you feel a border is needed, you haven't used enough shadow depth or white space.