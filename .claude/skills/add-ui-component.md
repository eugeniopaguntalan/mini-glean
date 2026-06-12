# Skill: Add a UI Component

## When to Use
- Adding a new component to `apps/web/components/`
- Building a new page in `apps/web/app/`
- Connecting a component to the backend

---

## Steps

1. Define the type in `packages/shared/types.ts`
2. Add the API call to `lib/api.ts` — never fetch inside a component
3. If stateful, create a hook in `hooks/` — component stays dumb
4. Build the component in `components/`
5. Add `"use client"` only if it needs event handlers or hooks
6. Handle all three async states: loading, empty, error

---

## Conventions

**Structure**
- Pages: `app/` — Server Components by default
- Components: `components/`
- Data hooks: `hooks/`
- API calls: `lib/api.ts`
- Types: `packages/shared/types.ts`

**TypeScript**
- No `any` — ever
- Props interface defined above every component
- Import types from `@/types`

**State Ownership**
- Hooks own state
- Components just render props
- Lift state only when two siblings share data
- Only two data-fetching hooks: `useDocuments` and `useChat`

**MD3 Styling**
- Tokens from `lib/theme.ts` — no raw hex
- Cards → `rounded-xl`
- Buttons/inputs → `rounded-full`
- Chips → `rounded-md`
- Hover → `bg-primary/8`
- See `skills/material-design-3.md` for full reference

---

## Rules
- No `fetch()` inside components — always `lib/api.ts`
- No `"use client"` by default — add only when required
- Every list view must handle: loading skeleton, empty state, error state
- No inline styles — Tailwind only
- No raw hex or arbitrary values — MD3 tokens only

---

## Checklist
- [ ] Type defined in `packages/shared/types.ts`
- [ ] API call in `lib/api.ts`
- [ ] Stateful logic in a hook — not in the component
- [ ] `"use client"` only where necessary
- [ ] MD3 tokens used throughout
- [ ] Loading, empty, and error states handled
- [ ] No `any` types