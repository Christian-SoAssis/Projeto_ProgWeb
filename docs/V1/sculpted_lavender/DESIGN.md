# Design System Document: The Sculpted Professional

## 1. Overview & Creative North Star: "The Digital Monolith"
This design system moves away from the flat, ephemeral nature of modern web interfaces toward a tactile, "physical" presence. The Creative North Star is **The Digital Monolith**—a philosophy where the interface is not a series of layers, but a single, continuous piece of material (Lavender Dust) that has been expertly sculpted, debossed, and extruded. 

We avoid the "template" look by treating the dashboard as a living organism. Through intentional asymmetry and the use of monochromatic depth, we create a high-end, editorial experience that feels permanent, weighted, and premium.

---

## 2. Colors & Surface Philosophy
The soul of this system lies in the subtle interplay of light and shadow on a monochromatic base. We do not use borders; we use physics.

### Palette Highlights
- **Background (Base):** `#d0ccdc` (Lavender Dust) — This is our "stone." All elements are carved from this.
- **Accent (Mint):** `#1a9878` (Primary) — Reserved for high-value actions and success indicators.
- **Surface Tiers:**
    - `surface_container_lowest`: `#ffffff` (The "Highlight" light source)
    - `surface_dim`: `#dcd8e8` (The "Shadow" depth)
    - `primary`: `#006c53` (Deep Mint for contrast)

### The "No-Line" Rule
**Borders are strictly prohibited.** To define a section, you must use a tonal shift or a sculptural transition. If two areas must be separated, use a shift from `surface` to `surface_container_low`. A 1px line is a failure of form; let the shadows do the work.

### Signature Textures
For Mint accents, use a linear gradient: `primary` (#006c53) to `primary_container` (#74e2be) at a 135-degree angle. This adds a "jewel-like" finish to the sculpted stone environment.

---

## 3. Typography: Editorial Precision
We pair the geometric friendliness of **Plus Jakarta Sans** with the technical rigor of **DM Mono**.

- **Display & Headlines (Plus Jakarta Sans):** Use large scales (`display-lg` at 3.5rem) with tight letter-spacing (-0.02em) to create an editorial, high-fashion feel.
- **Data & Stats (DM Mono):** All numerical values, timestamps, and professional metrics must use DM Mono. This conveys "Pro-Tools" accuracy and contrasts beautifully against the soft UI.
- **Visual Hierarchy:** Headlines should be `on_surface` (#1b1a26), while labels use `on_surface_variant` (#47464c) to pull back and let the sculpted shapes breathe.

---

## 4. Elevation & Depth (The Neomorphic Spec)
Neomorphism fails when it is too "noisy." We use a restrained, high-end approach to light physics.

### The Layering Principle (Elevated)
For "Elevated" cards (Stats, Professional Profiles), use two shadows:
- **Light:** Top-Left, -8px -8px, 16px blur, Color: `#ffffff` (at 70% opacity).
- **Dark:** Bottom-Right, 8px 8px, 16px blur, Color: `#b8b4c5` (a darker tint of Lavender Dust).

### The Inset Principle (Concave)
For "Inset" areas (Search inputs, Progress tracks, Sidebar active states), use internal shadows:
- **Light:** Internal Top-Left, -4px -4px, 10px blur, Color: `#ffffff`.
- **Dark:** Internal Bottom-Right, 4px 4px, 10px blur, Color: `#b8b4c5`.

### Glassmorphism & Depth
When a modal or floating menu is required, use `surface_container_lowest` with a 20px `backdrop-blur` and 40% opacity. This creates a "Frosted Lavender" effect that maintains the 3D illusion without breaking the monochromatic flow.

---

## 5. Components

### Sidebar (240px)
- **Base:** Matches `background` (#d0ccdc).
- **Active State:** Use the **Inset Principle**. The active menu item should look "pressed" into the sidebar, with text shifting to `primary` (#1a9878).
- **Spacing:** Use `spacing.4` (1.4rem) for vertical padding between items to ensure an airy, premium feel.

### Stats Cards (Elevated)
- **Geometry:** `roundedness.xl` (1.5rem).
- **Content:** Headline in `Plus Jakarta Sans`, Data Point in `DM Mono` (Mint Green).
- **Note:** No dividers. Use `spacing.6` to separate the icon from the metric.

### Buttons
- **Primary:** Elevated Mint gradient. On hover, the shadow softens (blur increases to 24px).
- **Tertiary:** Flat text with an "Inset" state only on active press.

### Progress Tracks & Charts
- **Track:** `Inset Principle` using a long, horizontal pill shape.
- **Fill:** `primary` (#1a9878) with a subtle inner-glow to make it look like liquid neon inside a stone groove.

### Input Fields
- **Style:** Pure Inset.
- **Focus State:** The "Ghost Border" fallback—a 1px glow using `primary` at 20% opacity to signal activity without adding a hard edge.

---

## 6. Do's and Don'ts

### Do:
- **Use "Lavender Dust" for everything:** The background, the cards, and the buttons should all be the same hex code; only the shadows create the shape.
- **Trust the White Space:** Use the `spacing.16` (5.5rem) scale for major section margins. High-end design needs room to breathe.
- **Use DM Mono for Numbers:** It provides the "Professional Dashboard" utility that anchors the soft aesthetic.

### Don't:
- **Don't use pure black shadows:** This will make the UI look "dirty." Always use a tinted shadow (#b8b4c5).
- **Don't use sharp corners:** Neomorphism relies on the "Surface Tension" of rounded edges. Use `roundedness.lg` as your minimum.
- **Don't use dividers:** If you feel the need to separate two lists, increase the vertical gap or change the background tone by 2%. Never draw a line.