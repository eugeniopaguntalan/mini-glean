# Skill: Add a FastAPI Endpoint

## When to Use
- Adding a new route to `apps/api/`
- Modifying an existing route's request/response shape
- Adding a streaming or background task endpoint

---

## Steps

1. Define request/response schemas in `apps/api/schemas.py` — Pydantic with explicit types
2. Write business logic in `apps/api/services/` — never in the router
3. DB access goes through `apps/api/repositories/` — never in services directly
4. Create or update the router in `apps/api/routers/`
5. Map exceptions to HTTP status codes in the router
6. Register the router in `apps/api/main.py` if new
7. If schema changed, create an Alembic migration
8. Add a test in `apps/api/tests/`

---

## Conventions

**Structure**
- Schemas: `apps/api/schemas.py`
- Business logic: `apps/api/services/<name>_service.py`
- Database access: `apps/api/repositories/<name>_repository.py`
- Routes: `apps/api/routers/<resource>.py`
- Custom exceptions: `apps/api/services/exceptions.py`

**Layer Responsibilities**
- Router: parse request, call service, map exceptions to HTTP codes, return response
- Service: orchestrate logic, call repositories, call LLM service, raise domain exceptions
- Repository: execute SQL queries, return models or dicts — no business logic

**Dependency Flow**

```text
Router → Service → Repository → Supabase (Postgres + pgvector)
→ LLM Service → OpenAI
```

---

## Rules
- No business logic in routers — routers are HTTP adapters only
- No raw SQL in services — all DB access through repositories
- No `Any` type in schemas — be explicit
- All exceptions defined in `services/exceptions.py`
- New env vars must be added to `.env.example`
- Schema changes require an Alembic migration
- Use `status.HTTP_201_CREATED` for resource creation, `204` for deletes

---

## Status Code Reference

| Situation | Code |
|---|---|
| Created a resource | 201 |
| Accepted async job | 202 |
| Deleted (no body) | 204 |
| Validation error | 400 |
| Not found | 404 |
| Wrong content type | 415 |
| Parse/processing failure | 422 |
| Server error | 500 |

---

## Special Patterns
- **Background task**: Use `BackgroundTasks` for anything > 2 seconds (PDF parsing, URL scraping)
- **Streaming**: Use `StreamingResponse` with `text/event-stream` for chat responses
- **File upload**: Use `UploadFile` with explicit size and content-type validation
- **Database session**: Inject via `Depends(get_session)` — never create manually

---

## Checklist
- [ ] Schema in `schemas.py` with explicit types
- [ ] Logic in `services/` — router is HTTP-only
- [ ] DB access in `repositories/` — services don't write SQL
- [ ] Exceptions in `services/exceptions.py`
- [ ] Router registered in `main.py`
- [ ] Alembic migration created (if schema changed)
- [ ] New env vars in `.env.example`
- [ ] Happy path + error path test written
- [ ] `ruff check .` passes

