# Skill: Code Review

## When to Use
- Reviewing any PR before merge
- Self-reviewing before pushing

---

## All Code
- [ ] Does one thing — split if it does two
- [ ] Error cases handled — no silent failures
- [ ] No hardcoded values that should be constants or env vars
- [ ] Diff is understandable without extra context

---

## Backend
- [ ] Router does HTTP only — no business logic
- [ ] Service calls repositories for DB access — no raw SQL in services
- [ ] Repository handles queries only — no business logic
- [ ] All Pydantic models have explicit types — no `Any`
- [ ] OpenAI called only through `services/llm.py`
- [ ] DB accessed only through `repositories/`
- [ ] Async functions don't block — no sync calls in async context
- [ ] New env vars documented in `.env.example`
- [ ] Schema changes have an Alembic migration

---

## RAG / AI Specific
- [ ] Chunk size/overlap not changed without retrieval quality justification
- [ ] Every AI response includes `source_doc_ids`
- [ ] LLM temperature is 0.0 for factual Q&A
- [ ] Tool docstrings are clear and specific
- [ ] No prompt strings hardcoded outside `prompts/`

---

## Frontend
- [ ] No `any` types
- [ ] No `fetch()` inside components — `lib/api.ts` only
- [ ] `"use client"` only where needed
- [ ] MD3 tokens used — no raw hex
- [ ] Loading, empty, error states handled

---

## Database
- [ ] New tables or columns have an Alembic migration
- [ ] Indexes added for frequently queried columns
- [ ] CASCADE behavior is correct on foreign keys
- [ ] No raw SQL outside repository files

---

## Tests
- [ ] External services mocked at repository boundary
- [ ] New code has at least happy path + error path test
- [ ] New components have at least a render test

---

## Review Etiquette
- Ask before assuming: "Did you consider X?" not "This is wrong"
- Prefix minor style comments with `nit:`
- Approve when good enough — don't block on perfection