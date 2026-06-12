# Skill: Material Design 3

## When to Use
- Building or styling any UI component
- Choosing colors, typography, shape, or elevation
- Deciding which MD3 component pattern to use

---

## Token Source
All tokens defined in `apps/web/lib/theme.ts` and extended in `tailwind.config.ts`.
Never use raw hex — always use semantic token names.

---

## Colors (Semantic Roles)

| Token | Usage |
|---|---|
| `primary` / `on-primary` | Primary buttons, active states |
| `primary-container` / `on-primary-container` | Badges, filled chips |
| `secondary-container` / `on-secondary-container` | Tab highlights, secondary badges |
| `surface` / `on-surface` | Default backgrounds, text |
| `surface-variant` / `on-surface-variant` | Muted backgrounds, secondary text |
| `error` / `on-error` | Error states, destructive actions |
| `outline` | Input borders |
| `outline-variant` | Card borders, dividers |

---

## Typography Scale

| Role | Size / Leading / Weight / Tracking |
|---|---|
| Display Large | 57px / 64px / normal / -0.25px |
| Headline Large | 32px / 40px / normal |
| Title Large | 22px / 28px / normal |
| Title Medium | 16px / 24px / medium / 0.15px |
| Body Large | 16px / 24px / normal / 0.5px |
| Body Medium | 14px / 20px / normal / 0.25px |
| Label Large | 14px / 20px / medium / 0.1px |
| Label Medium | 12px / 16px / medium / 0.5px |
| Label Small | 11px / 16px / medium / 0.5px |

---

## Shape (Corner Radius)

| Shape | Tailwind | Use For |
|---|---|---|
| None | `rounded-none` | — |
| Extra Small | `rounded-sm` | — |
| Small | `rounded-md` | Chips, text fields |
| Medium | `rounded-xl` | Cards |
| Large | `rounded-2xl` | Dialogs, sheets |
| Full | `rounded-full` | Buttons, FABs |

---

## Elevation

| Level | Tailwind | Use For |
|---|---|---|
| 0 | (none) | Flat surfaces |
| 1 | `shadow-sm` | Cards |
| 2 | `shadow-md` | Dropdowns, menus |
| 3 | `shadow-lg` | Dialogs, modals |

---

## State Layers

| State | Overlay |
|---|---|
| Hover | `bg-primary/8` |
| Focus | `bg-primary/12` |
| Pressed | `bg-primary/16` |
| Disabled | `opacity-50` |

---

## Component → MD3 Mapping

| Component | Card Type | Rounding | Interaction |
|---|---|---|---|
| DocumentCard | Elevated | `rounded-xl` | `hover:shadow-md` |
| UploadPanel | Outlined | `rounded-xl` | `hover:border-primary` |
| ChatMessage (user) | — | `rounded-xl rounded-br-sm` | — |
| ChatMessage (AI) | Elevated | `rounded-xl rounded-bl-sm` | — |
| SourceCitation | Assist Chip | `rounded-md` | `hover:bg-surface-variant` |
| Primary button | Filled | `rounded-full` | `hover:shadow-md` |
| Secondary button | Outlined | `rounded-full` | `hover:bg-primary/8` |
| Text field | Outlined | `rounded-md` | `focus:border-primary` |

---

## Rules
- Never use raw hex — always token names
- `rounded-full` only for buttons and inputs
- `rounded-xl` for cards
- `rounded-md` for chips and text fields
- Dark mode: swap surface/on-surface — don't manually invert
- Font: Inter (system-level Roboto Flex alternative)