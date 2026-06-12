# Skill: Code Standards

## When to Use
- Unsure about naming, file placement, or style
- Starting a new file or module
- Reviewing for consistency

---

## Python (apps/api)

**Formatter**: `ruff format` — run before every commit
**Linter**: `ruff check` — zero warnings policy
**Type hints**: Required on all function signatures
**Docstrings**: Only on public service methods and tools

**Naming**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

**Layer Naming**
- Routers: `<resource>.py` — e.g. `documents.py`, `chat.py`
- Services: `<name>_service.py` — e.g. `document_service.py`
- Repositories: `<name>_repository.py` — e.g. `chunk_repository.py`
- Tools: `<verb>_<noun>.py` — e.g. `search_knowledge_base.py`
- Prompts: `<purpose>.py` — e.g. `qa.py`, `summarize.py`

**Structure Rules**
- Router: HTTP concerns only
- Service: business logic, orchestration
- Repository: database queries, returns models or dicts
- Tool: agent capability, calls repositories and LLM service
- Never call OpenAI outside `services/llm.py`
- Never write SQL outside `repositories/`

**Error Handling**
- Custom exceptions in `services/exceptions.py`
- Services raise domain exceptions
- Routers map to HTTP status codes
- Repositories raise only if DB operation fails

---

## TypeScript (apps/web)

**Strict mode**: Enabled — no exceptions
**No `any`**: Use `unknown` and narrow, or define the type
**Formatter**: Prettier

**Naming**
- Components: `PascalCase.tsx`
- Utilities: `camelCase.ts`
- Hooks: `use` prefix — `useDocuments.ts`
- Constants: `UPPER_SNAKE_CASE`

**Component Rules**
- Props interface above every component
- No inline styles — Tailwind only
- No fetch inside components — `lib/api.ts` only
- Server Components by default

---

## Git

**Commit Format**

type(scope): short description

```text
Types: `feat` | `fix` | `refactor` | `test` | `chore` | `docs`
```

**Branch Format**

type/short-description


**Rules**
- One logical change per commit
- Never commit `.env` — only `.env.example`
- Never commit `data/` folder
- Database migrations get their own commit: `chore(db): add tags column migration`

---

## Checklist
- [ ] File named correctly for its language and layer
- [ ] Placed in the right directory
- [ ] Follows naming conventions
- [ ] `ruff check .` / `npm run lint` passes
- [ ] Commit message follows format