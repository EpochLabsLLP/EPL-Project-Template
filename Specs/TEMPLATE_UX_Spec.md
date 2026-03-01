<!-- TEMPLATE: UX Spec
     Defines the user experience — screens, flows, components, design tokens.
     Required for projects with a user interface. Omit for backend/API/CLI projects.

     USAGE:
     1. Ensure PVD and Engineering Spec are FROZEN
     2. Copy this file to: Specs/{Abbrev}_UX_Spec_DRAFT.md
     3. Replace all {placeholders} with real values
     4. Assign UX-N.M identifiers (N = PVD feature, M = screen/flow sequence)
     5. Change Status to FROZEN and rename: {Abbrev}_UX_Spec_v1.md
     6. Proceed to Blueprint

     TRACEABILITY: UX-N.M traces directly to PVD-N (not through ES).
     UX crosses module boundaries — a single screen may involve multiple ES modules.
     Example: UX-3.1 = Screen/flow #1 for PVD Feature #3. -->

# {ProjectName} — UX Spec

| Field | Value |
|-------|-------|
| **Version** | {N} |
| **Status** | DRAFT / FROZEN |
| **Date** | {YYYY-MM-DD} |
| **Author** | {Name} |
| **Implements** | `Specs/{Abbrev}_PVD_v{N}.md` (or PRD) |
| **Governed by** | CLAUDE.md, SDD Framework |

---

## 1. Design Principles

{3-5 design principles that guide all UX decisions for this project.}

1. **{Principle 1}:** {Description and rationale}
2. **{Principle 2}:** {Description and rationale}
3. **{Principle 3}:** {Description and rationale}

---

## 2. Screen Inventory

<!-- Assign UX-N.M identifiers. N = PVD feature, M = screen sequence.
     Each screen spec should include: purpose, layout, key elements,
     states (loading, empty, error, populated), and interactions. -->

### UX-1.1: {Screen Name}
- **Implements:** PVD-1
- **Purpose:** {What the user accomplishes on this screen}
- **Entry points:** {How user arrives here}
- **Key elements:**
  - {Element 1 — description and behavior}
  - {Element 2 — description and behavior}
- **States:**
  - Loading: {what user sees while data loads}
  - Empty: {what user sees when no data exists}
  - Populated: {the normal state}
  - Error: {what user sees on failure}
- **Exit points:** {Where user can go from here}

### UX-1.2: {Screen Name}
- **Implements:** PVD-1
{Continue pattern...}

### UX-2.1: {Screen Name}
- **Implements:** PVD-2
{Continue pattern...}

---

## 3. Navigation Flows

{How screens connect to each other. Include primary navigation structure
and key user journeys.}

### Navigation Structure
```
{ASCII navigation map}

Example:
  Login (UX-1.1) ──► Dashboard (UX-2.1) ──► Settings (UX-3.1)
                                          ──► Detail View (UX-2.2)
```

### Key User Journeys
{The most important paths through the UI, end to end.}

---

## 4. Component Library

{Reusable UI components used across screens.}

### {Component Name}
- **Usage:** {Where this component appears}
- **Variants:** {Different states/sizes/modes}
- **Props/Inputs:** {What configures this component}
- **Behavior:** {Interaction patterns}

---

## 5. Design Tokens

### Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | {hex} | {where used} |
| `--color-secondary` | {hex} | {where used} |
| `--color-background` | {hex} | {where used} |
| `--color-surface` | {hex} | {where used} |
| `--color-text-primary` | {hex} | {where used} |
| `--color-text-secondary` | {hex} | {where used} |
| `--color-error` | {hex} | {where used} |
| `--color-success` | {hex} | {where used} |

### Typography
| Token | Value | Usage |
|-------|-------|-------|
| `--font-family-primary` | {font} | {body text, etc.} |
| `--font-family-heading` | {font} | {headings} |
| `--font-size-xs` | {size} | {labels, captions} |
| `--font-size-sm` | {size} | {secondary text} |
| `--font-size-md` | {size} | {body text} |
| `--font-size-lg` | {size} | {subheadings} |
| `--font-size-xl` | {size} | {headings} |

### Spacing
| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | {size} | {tight spacing} |
| `--space-sm` | {size} | {compact spacing} |
| `--space-md` | {size} | {default spacing} |
| `--space-lg` | {size} | {section spacing} |
| `--space-xl` | {size} | {major section spacing} |

---

## 6. Responsive Breakpoints

| Breakpoint | Width | Layout Behavior |
|-----------|-------|-----------------|
| Mobile | {e.g., < 768px} | {description} |
| Tablet | {e.g., 768-1024px} | {description} |
| Desktop | {e.g., > 1024px} | {description} |

---

## 7. Interaction Patterns

{Standard interaction behaviors used across the product.}

### {Pattern Name} (e.g., Form Submission)
- **Trigger:** {what initiates this interaction}
- **Feedback:** {what the user sees during processing}
- **Success:** {what happens on success}
- **Failure:** {what happens on failure}

---

## 8. Animation & Transitions

{Motion design principles and specific animation definitions.}

| Transition | Duration | Easing | Context |
|-----------|----------|--------|---------|
| {Page transition} | {ms} | {easing} | {when used} |
| {Modal open} | {ms} | {easing} | {when used} |
| {Loading spinner} | {ms} | {easing} | {when used} |

---

## 9. Accessibility Requirements

- **WCAG Target:** {2.1 AA / 2.1 AAA}
- **Keyboard navigation:** {Full keyboard support for all interactive elements}
- **Screen reader support:** {ARIA labels, semantic HTML, live regions}
- **Color contrast:** {Minimum ratios per WCAG level}
- **Focus management:** {Focus trapping in modals, logical tab order}
- **Motion preferences:** {Respect prefers-reduced-motion}

---

## 10. Error & Loading States

### Global Error Patterns
- **Network error:** {what user sees, retry behavior}
- **Server error (5xx):** {user-facing message, recovery path}
- **Client error (4xx):** {field-level vs page-level error display}
- **Session expired:** {behavior, redirect path}

### Loading Patterns
- **Initial load:** {skeleton screens / spinner / progressive}
- **Data refresh:** {indicator style, stale data handling}
- **Action pending:** {button state, progress indicator}

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1 | {YYYY-MM-DD} | Initial UX specification | {Author} |
