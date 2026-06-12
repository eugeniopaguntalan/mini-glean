# Skill: Write a Test

## When to Use
- Adding a new service, tool, router, or component
- Fixing a bug — write the test that would have caught it first
- Expanding coverage for an existing module

---

## Steps

**Backend**
1. Create file in `apps/api/tests/` mirroring source structure
2. Mock external dependencies: OpenAI, database session
3. Write at minimum: one happy path, one error path
4. Use `pytest.mark.asyncio` for async services

**Frontend**
1. Create file alongside component: `ComponentName.test.tsx`
2. Test rendering with expected props
3. Test user interactions via `@testing-library/react`
4. Mock `lib/api.ts` — never hit real endpoints

---

## Conventions

**Backend**
- Framework: `pytest` + `pytest-asyncio`
- Mocking: `unittest.mock.patch` + `AsyncMock`
- Fixtures in `apps/api/tests/fixtures/`
- Name pattern: `test_<action>_<expected_outcome>`

**Frontend**
- Framework: Jest + React Testing Library
- Query by role/text — not by class or test ID
- Name pattern: `it('<does what when condition>')`

---

## What to Mock — Always
- OpenAI API calls (embeddings + LLM)
- Database session and repository methods
- External HTTP calls
- File system operations

## What NOT to Mock
- Pydantic schema validation
- Pure utility functions
- In-memory data transformations

---

## Mocking the Database

```python
# Mock the repository, not the database session directly
with patch("services.document_service.document_repository") as mock_repo:
    mock_repo.get_by_id = AsyncMock(return_value=mock_document)
    result = await document_service.get("abc-123")
```
Not this:

```python
# ❌ Don't mock SQLAlchemy internals — too brittle
with patch("sqlalchemy.ext.asyncio.AsyncSession.execute"):
    ...
```

### Integration Tests vs Unit Tests

| | Unit Tests | Integration Tests |
|--|------------|-------------------|
| External services | Mocked | Real |
| Speed | Fast (< 1s each) | Slow (2-10s each) |
| Cost | Free | Costs money (OpenAI) |
| When to run | Every push | Before merge to main |
| Location | `tests/unit/` | `tests/integration/` |

### Rules
- Never call real OpenAI or Supabase in unit tests
- One test file per service or component
- Test behaviour, not implementation
- Mock at the repository boundary — not deeper
- If a test needs more than 3 mocks, the code under test is doing too much — refactor first
- Integration tests: see docs/integration-test.md for scenarios

### Checklist
- Happy path covered
- Error/edge case covered
- External services mocked (at repository boundary)
- Test name describes behaviour, not method name
- pytest / npm test passes locally