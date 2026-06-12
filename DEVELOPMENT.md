# Development Guide

> Comprehensive guide for developing MiniGlean locally

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Standards](#code-standards)
- [Database Management](#database-management)
- [Common Tasks](#common-tasks)
- [Debugging](#debugging)
- [Deployment](#deployment)

## Prerequisites

### Required

- **Python 3.11+** — Backend runtime
- **Node.js 20+** — Frontend runtime
- **Docker Desktop** — For PostgreSQL with pgvector
- **OpenAI API Key** — For embeddings and chat

### Recommended

- **VS Code** — IDE with Python and TypeScript extensions
- **Postman/curl** — API testing
- **psql** — PostgreSQL client for database inspection

## Initial Setup

### 1. Clone and Environment

```bash
git clone <repository-url>
cd MiniGlean
```

### 2. Backend Setup

```bash
cd apps/api

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `apps/api/.env` and add:

```bash
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/miniglean
```

### 3. Database Setup

```bash
# Start PostgreSQL with pgvector
docker-compose up db -d

# Run migrations
cd apps/api
alembic upgrade head

# Verify connection
psql postgresql://postgres:postgres@localhost:5432/miniglean -c "SELECT 1"
```

### 4. Frontend Setup (Milestone 5+)

```bash
cd apps/web

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local
```

Edit `apps/web/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
MiniGlean/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── alembic/           # Database migrations
│   │   │   └── versions/      # Migration files
│   │   ├── prompts/           # LLM prompt templates
│   │   │   └── qa.py          # QA system prompt
│   │   ├── repositories/      # Database access layer
│   │   │   ├── chunk_repository.py
│   │   │   └── document_repository.py
│   │   ├── routers/           # API endpoints
│   │   │   ├── health.py
│   │   │   ├── documents.py
│   │   │   └── chat.py
│   │   ├── services/          # Business logic
│   │   │   ├── parser.py      # PDF/URL/note parsing
│   │   │   ├── chunker.py     # Text chunking
│   │   │   ├── embedder.py    # OpenAI embeddings
│   │   │   ├── retriever.py   # Vector search
│   │   │   ├── llm.py         # OpenAI chat completions
│   │   │   ├── chat_service.py # RAG orchestration
│   │   │   ├── document_service.py
│   │   │   └── exceptions.py
│   │   ├── tests/
│   │   │   ├── unit/          # Unit tests (mocked)
│   │   │   ├── integration/   # Integration tests
│   │   │   └── fixtures/      # Test fixtures
│   │   ├── config.py          # Settings management
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── models.py          # ORM models
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── main.py            # FastAPI app
│   └── web/                   # Next.js frontend (Milestone 5)
│       ├── app/               # App Router pages
│       ├── components/        # React components
│       └── lib/               # Utilities
├── docs/                      # Architecture docs
│   ├── architecture.md
│   ├── database.md
│   ├── deployment.md
│   ├── environment-variables.md
│   └── integration-test.md
├── milestones/                # Development milestones
│   ├── 01-setup.md
│   ├── 02-ingestion.md
│   ├── 03-rag-core.md        # ✅ Current
│   ├── 04-chat-agent.md
│   ├── 05-ui-polish.md
│   └── 06-demo-ready.md
├── docker-compose.yml         # Local dev orchestration
├── CLAUDE.md                  # AI assistant reference
├── DEVELOPMENT.md             # This file
└── README.md                  # User-facing docs
```

## Development Workflow

### Starting the Backend

```bash
cd apps/api
source .venv/bin/activate
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Starting the Frontend (Milestone 5+)

```bash
cd apps/web
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Development Loop

1. **Make code changes** in your editor
2. **Run tests** for the changed module
3. **Lint code** with ruff (backend) or eslint (frontend)
4. **Test manually** via API docs or frontend
5. **Commit** with descriptive message
6. **Push** to GitHub

### Hot Reload

- **Backend:** uvicorn auto-reloads on `.py` file changes
- **Frontend:** Next.js auto-reloads on component changes
- **Database:** Requires manual migration for schema changes

## Testing

### Unit Tests

**Backend:**

```bash
cd apps/api

# Run all unit tests
.venv/bin/python -m pytest tests/unit/ -v

# Run specific test file
.venv/bin/python -m pytest tests/unit/test_chat_service.py -v

# Run with coverage
.venv/bin/python -m pytest tests/unit/ --cov=services --cov-report=html

# Run specific test
.venv/bin/python -m pytest tests/unit/test_llm.py::test_generate_answer_returns_content -v
```

**Test Structure:**
- All external services (OpenAI, database) are mocked
- Use `AsyncMock` for async functions
- Use `@pytest.mark.asyncio` for async tests
- Fixtures in `tests/fixtures/`

**Frontend (Milestone 5):**

```bash
cd apps/web
npm test
```

### Integration Tests

```bash
cd apps/api
.venv/bin/python -m pytest tests/integration/ --env=staging -v
```

Integration tests require:
- Real database connection
- OpenAI API key (uses real API, minimal calls)
- Longer timeout limits

### Manual Testing

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Upload Document:**
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@test.pdf"
```

**Chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is in my documents?"}'
```

## Code Standards

### Backend (Python)

**Linting:**

```bash
cd apps/api

# Check for issues
.venv/bin/ruff check .

# Auto-fix issues
.venv/bin/ruff check . --fix

# Format code
.venv/bin/ruff format .
```

**Style Guide:**
- Follow PEP 8
- Use type hints for all function signatures
- Docstrings for public functions (Google style)
- Maximum line length: 88 characters (ruff default)
- Use `async/await` for I/O operations
- Repository pattern for database access

**Example:**

```python
async def retrieve(
    question: str, 
    chunk_repo: ChunkRepository, 
    top_k: int = 5
) -> List[RetrievedChunk]:
    """
    Retrieve relevant chunks for a question
    
    Args:
        question: The user's question
        chunk_repo: Repository for chunk database access
        top_k: Maximum number of chunks to retrieve
        
    Returns:
        List of RetrievedChunk objects (may be empty)
    """
    # Implementation
```

### Frontend (TypeScript)

```bash
cd apps/web

# Lint
npm run lint

# Type check
npm run type-check

# Format
npm run format
```

**Style Guide:**
- Use functional components with hooks
- TypeScript strict mode enabled
- Material Design 3 components
- Tailwind CSS for styling
- Named exports for components

### Key Conventions

**Backend:**
- Never instantiate OpenAI client outside `services/llm.py` or `services/embedder.py`
- All database access through repositories
- Prompts in `prompts/` directory, not hardcoded
- Raise domain-specific exceptions from `services/exceptions.py`
- Use Pydantic models for validation in routers

**Frontend:**
- API calls centralized in `lib/api.ts`
- Shared types in `packages/shared/types.ts`
- Use App Router (`app/`), not Pages Router
- Server components by default, client components only when needed

**General:**
- Embedding model: `text-embedding-3-small` (1536 dimensions)
- LLM model: `gpt-4o` (temperature 0.0 for Q&A)
- Chunk size: 500 tokens, overlap: 50
- Similarity threshold: 0.3

## Database Management

### Migrations

**Create a new migration:**

```bash
cd apps/api
alembic revision -m "description of change"
```

Edit the generated file in `alembic/versions/`, then:

```bash
# Apply migration
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Check current version
alembic current

# View migration history
alembic history
```

**Migration Best Practices:**
- Always test migrations on local database first
- Include both `upgrade()` and `downgrade()` operations
- Never modify existing migrations that are in production
- Use batch operations for large data migrations

### Database Inspection

```bash
# Connect to database
psql postgresql://postgres:postgres@localhost:5432/miniglean

# List tables
\dt

# Describe table
\d documents

# View pgvector extension
\dx

# Sample query
SELECT id, filename, chunk_count FROM documents LIMIT 5;

# Check vector dimensions
SELECT id, LENGTH(embedding::text) FROM chunks LIMIT 1;
```

### Reset Database

```bash
# Drop and recreate database
docker-compose down -v
docker-compose up db -d
cd apps/api
alembic upgrade head
```

## Common Tasks

### Add a New API Endpoint

1. **Define schema** in `schemas.py`:
   ```python
   class MyRequest(BaseModel):
       field: str
   ```

2. **Create router** in `routers/my_router.py`:
   ```python
   from fastapi import APIRouter
   router = APIRouter(prefix="/my-endpoint", tags=["my-tag"])
   
   @router.post("", response_model=MyResponse)
   async def my_endpoint(request: MyRequest):
       # Implementation
   ```

3. **Register router** in `main.py`:
   ```python
   from routers import my_router
   app.include_router(my_router.router)
   ```

4. **Write tests** in `tests/unit/test_my_router.py`

### Add a New Service

1. **Create service** in `services/my_service.py`
2. **Define exceptions** if needed in `services/exceptions.py`
3. **Add repository** if database access needed
4. **Write unit tests** with mocked dependencies
5. **Update documentation**

### Add Environment Variable

1. **Add to `config.py`**:
   ```python
   class Settings(BaseSettings):
       MY_VAR: str = "default_value"
   ```

2. **Add to `.env.example`**:
   ```bash
   MY_VAR=example_value
   ```

3. **Document** in `docs/environment-variables.md`

### Ingest a Test Document

```bash
# Create a test PDF
cd apps/api
.venv/bin/python create_test_pdf.py

# Upload via API
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@test_document.pdf"
```

## Debugging

### Backend Debugging

**Enable debug logging:**

Edit `.env`:
```bash
LOG_LEVEL=DEBUG
```

**VS Code launch.json:**

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["main:app", "--reload"],
            "cwd": "${workspaceFolder}/apps/api",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/apps/api"
            }
        }
    ]
}
```

**Common Issues:**

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Activate venv: `source .venv/bin/activate` |
| Database connection fails | Check Docker: `docker-compose ps` |
| OpenAI API errors | Verify `OPENAI_API_KEY` in `.env` |
| Vector search returns empty | Check similarity threshold (0.3) |
| Tests fail on import | Install pytest: `pip install pytest pytest-asyncio` |

### Database Debugging

**View recent chunks:**
```sql
SELECT 
    c.id, 
    d.filename, 
    LEFT(c.content, 100) as preview
FROM chunks c
JOIN documents d ON c.document_id = d.id
ORDER BY c.created_at DESC
LIMIT 10;
```

**Check vector similarity:**
```sql
SELECT 
    id,
    content,
    embedding <=> '[0.1, 0.2, ...]'::vector AS distance
FROM chunks
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

### Frontend Debugging (Milestone 5+)

**Console logging:**
```typescript
console.log('Debug:', { variable });
```

**React DevTools:**
- Install React Developer Tools extension
- Inspect component state and props

## Deployment

See [docs/deployment.md](docs/deployment.md) for detailed deployment instructions.

### Quick Deploy Commands

**Backend (Railway):**
```bash
# Push triggers automatic deploy
git push origin main
```

**Frontend (Vercel):**
```bash
# Push triggers automatic deploy
git push origin main
```

**Database (Supabase):**
```bash
# Run migrations manually on production
DATABASE_URL=<supabase-url> alembic upgrade head
```

### Environment Variables

Required for each environment:

**Development:**
- See `.env.example` files

**Staging/Production:**
- Set via Railway/Vercel dashboard
- Never commit real credentials
- See `docs/environment-variables.md`

## Best Practices

### Version Control

- Commit frequently with clear messages
- Use feature branches for large changes
- Keep commits atomic (one logical change)
- Write descriptive commit messages

**Commit Message Format:**
```
type(scope): short description

Longer explanation if needed

- Bullet points for details
- Reference issue numbers: #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### Code Review

Before submitting a PR:
1. Run all tests locally
2. Run linter and fix all issues
3. Update documentation
4. Test manually via API docs
5. Write descriptive PR description

### Security

- Never commit `.env` files
- Use environment variables for secrets
- Validate all user input (Pydantic handles this)
- Sanitize file uploads
- Rate limit API endpoints (add in production)

## Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLAlchemy Async:** https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **pgvector:** https://github.com/pgvector/pgvector
- **OpenAI API:** https://platform.openai.com/docs
- **Next.js:** https://nextjs.org/docs
- **Material Design 3:** https://m3.material.io/

## Getting Help

1. Check this guide and other docs in `docs/`
2. Review milestone specs in `milestones/`
3. Check `CLAUDE.md` for project conventions
4. Search existing issues/PRs
5. Ask in project discussions

---

**Last Updated:** Milestone 3 (RAG Core)  
**Status:** Backend complete through chat endpoint
