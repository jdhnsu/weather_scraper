---
name: Atmospheric Intelligence
colors:
  surface: '#f9f9fd'
  surface-dim: '#d9dade'
  surface-bright: '#f9f9fd'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f7'
  surface-container: '#edeef1'
  surface-container-high: '#e7e8ec'
  surface-container-highest: '#e2e2e6'
  on-surface: '#191c1f'
  on-surface-variant: '#41474e'
  inverse-surface: '#2e3134'
  inverse-on-surface: '#f0f0f4'
  outline: '#72787f'
  outline-variant: '#c1c7cf'
  surface-tint: '#2d628c'
  primary: '#235a84'
  on-primary: '#ffffff'
  primary-container: '#40739e'
  on-primary-container: '#ecf4ff'
  inverse-primary: '#9acbfb'
  secondary: '#286292'
  on-secondary: '#ffffff'
  secondary-container: '#94c8ff'
  on-secondary-container: '#135483'
  tertiary: '#764f04'
  on-tertiary: '#ffffff'
  tertiary-container: '#92671f'
  on-tertiary-container: '#fff2e4'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#cee5ff'
  primary-fixed-dim: '#9acbfb'
  on-primary-fixed: '#001d32'
  on-primary-fixed-variant: '#0a4a73'
  secondary-fixed: '#cfe5ff'
  secondary-fixed-dim: '#99cbff'
  on-secondary-fixed: '#001d34'
  on-secondary-fixed-variant: '#004a78'
  tertiary-fixed: '#ffddb1'
  tertiary-fixed-dim: '#f3bd6d'
  on-tertiary-fixed: '#291800'
  on-tertiary-fixed-variant: '#624000'
  background: '#f9f9fd'
  on-background: '#191c1f'
  surface-variant: '#e2e2e6'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  group-label:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 20px
  body-base:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  control-label:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  table-cell:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 24px
  group-margin: 16px
  gutter: 16px
  control-gap: 12px
---

## Brand & Style
This design system is engineered for precision and reliability in data-heavy environments. The brand personality is authoritative yet accessible, designed to instill confidence in technical users overseeing complex scraping operations. 

The style is **Corporate / Modern**, leaning heavily into functional clarity. It prioritizes information density without sacrificing legibility. High-contrast elements and a structured hierarchy ensure that critical weather metrics and system statuses are digestible at a glance. The aesthetic avoids unnecessary ornamentation, focusing instead on the utility of the data through clean lines, systematic spacing, and a focused "Corporate Blue" palette.

## Colors
The palette is centered around a professional "Corporate Blue" that signals stability and trust. 

- **Primary & Secondary:** Used for active states, key action buttons, and progress indicators. Secondary blue provides subtle variance for depth.
- **Background & Surface:** A cool-toned off-white (`#f5f6fa`) serves as the canvas, while pure white (`#ffffff`) surfaces define the primary content containers.
- **Feedback:** Success green is reserved for completed scraping tasks and healthy system statuses. 
- **Borders:** A consistent light grey (`#dcdde1`) is used to define structural boundaries without creating visual noise.

## Typography
Inter is used across the system for its exceptional legibility in digital interfaces. 

- **Hierarchy:** We use bold, uppercase labels for Group Box headers to create clear visual anchors for different functional zones.
- **Data Display:** For coordinates, timestamps, or raw weather data strings, a monospaced font (JetBrains Mono) is used to maintain vertical alignment and readability.
- **Scaling:** The base size of 14px ensures density for professional dashboards while maintaining accessibility.

## Layout & Spacing
The layout follows a **Fixed Grid** philosophy within high-level containers, using a strict 4px baseline rhythm.

- **Structure:** Content is organized using `QGroupBox` for logical control segments and `QTabWidget` for high-level view switching (e.g., Map View, Data Table, Logs).
- **Margins:** 24px padding is applied to the main dashboard edges, with 16px gutters between adjacent data cards or group boxes.
- **Reflow:** On smaller screens, the side-panel controls collapse into a top-bar or drawer to prioritize the main data visualization area.

## Elevation & Depth
Depth is communicated through **Tonal Layers** and subtle shadows rather than aggressive elevation.

- **Primary Surface:** The background sits at the lowest level.
- **Cards/Group Boxes:** These use a subtle 4px blur shadow with 5% opacity to lift them slightly off the background.
- **Borders:** Every container has a 1px solid border in `#dcdde1` to reinforce the structure.
- **Interactive Elements:** Buttons and input fields use a slight inset shadow on press to provide tactile feedback.

## Shapes
A "Soft" rounding strategy is applied throughout the design system. 

- **Containers:** All Group Boxes, Tabs, and Cards use a 6px (`0.375rem`) corner radius.
- **Controls:** Buttons and input fields follow the same 6px radius for consistency.
- **Progress Bars:** These feature fully rounded (pill-shaped) caps to differentiate them from structural containers.

## Components
- **Buttons:** Solid primary blue for main actions (e.g., "Start Scraping"). Secondary actions use an outlined style with a 1px border.
- **Tables:** Rows feature alternating colors (`#f9f9f9` for even rows) to help track data across wide screens. Header cells are slightly darker with bold text.
- **Progress Bars:** Use the Success Green (`#2ecc71`) for completion and Primary Blue for active states. The track should be a light grey with an inner shadow.
- **Group Boxes:** These must have a clear 1px border and the title should be positioned either within the top border or immediately above it in the `group-label` type style.
- **Input Fields:** 14px text height, 8px internal padding, and a blue focus ring (2px) when active.
- **Status Badges:** Small, rounded chips used in tables to show scraper health (e.g., "Online," "Idle," "Error").