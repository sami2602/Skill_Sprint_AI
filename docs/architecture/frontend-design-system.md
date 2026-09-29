# SkillSprint AI — Frontend Architecture & Design System Specification

## Executive Overview
The **SkillSprint AI** frontend is an enterprise-grade React 18 Single-Page Application (SPA) engineered with TypeScript, Vite, Tailwind CSS, Framer Motion, and Recharts. It provides a polished, humanized, and trustworthy interface for corporate training leads, compliance reviewers, operational managers, and onboarding employees.

---

## Brand & Design Tokens

### Color Palette
- **Obsidian Navy (`#0B1220`)**: Deep enterprise canvas, sidebars, executive cards.
- **Cloud White (`#F7F8FA`)**: Workspace backgrounds, clean content containers.
- **Electric Blue (`#2563EB`)**: Primary interactive controls, focus rings, primary CTAs.
- **Intelligent Teal (`#14B8A6`)**: Ground-Truth validation badges, Python engine callouts.
- **Success (`#16A34A`)**: 100% mandatory coverage, verified decisions, passed tests.
- **Warning (`#D97706`)**: Review queue alerts, manual review flags, policy updates.
- **Danger (`#DC2626`)**: Mandatory requirement tags, critical severity badges.
- **AI Accent (`#7C3AED`)**: Sparingly applied for GenAI generation indicators and Gemini API badges.

### Typography Hierarchy
- **Headings**: `Manrope` (Geometric, precise, editorial font family)
- **Body & UI Controls**: `Inter` (Legible, ergonomic interface typeface)
- **Technical Metadata & Code**: `JetBrains Mono` (Document IDs, section codes, JSON payloads)

---

## Component Architecture

1. **Application Shell**:
   - Collapsible enterprise sidebar with role-filtered navigation items.
   - Sticky top bar with current page title, role context switcher, search bar, system status indicator, and notification drawer.
2. **Flagship Verification Inspector**:
   - `SideBySideInspector`: Visualizes the 5-stage verification drill-down flow:
     `Expected (DB Matrix) → Generated (GenAI Output) → Python Validation (Ground-Truth) → Citation Evidence → Decision`
3. **Policy Diff Viewer**:
   - `PolicyDiffViewer`: Displays document version transitions (e.g. `v1.0` → `v2.0`) and provides selective regeneration controls.
4. **Reviewer Override Module**:
   - Enforces a mandatory override reason text input whenever a reviewer overrides a system compliance decision.

---

## Accessibility & Responsive Breakpoints
- **Focus Indicators**: `focus-visible:ring-2 focus-visible:ring-electric-600`
- **Motion Controls**: Explicit `@media (prefers-reduced-motion: reduce)` rules disabling heavy CSS animations.
- **Screen Breakpoints**: `320px`, `375px`, `768px`, `1024px`, `1280px`, `1440px`, `1920px`.
