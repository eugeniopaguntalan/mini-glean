# Milestone 1 — Project Setup

## Goal

A working monorepo with frontend, backend, and database running locally via Docker. No AI functionality yet — just infrastructure, database schema, and the ability to confirm everything connects.

## Done When

* [ ] Monorepo structure created with all directories
* [ ] `docker-compose up` starts Next.js + FastAPI + Postgres (pgvector)
* [ ] Next.js home page loads at `http://localhost:3000`
* [ ] FastAPI docs load at `http://localhost:8000/docs`
* [ ] `GET /health` returns `{ "status": "ok", "database": "connected" }`
* [ ] pgvector extension enabled in local Postgres
* [ ] Alembic configured and initial migration creates `documents` + `chunks` tables
* [ ] SQLAlchemy models defined for Document and Chunk
* [ ] Repository classes scaffolded (document + chunk)
* [ ] Database session management with async SQLAlchemy
* [ ] `pydantic-settings` loads and validates env vars at startup — fails fast if missing
* [ ] `.env.example` committed with all variable names
* [ ] Linting passes: `ruff check .` and `npm run lint`
* [ ] README updated with setup instructions

## Out of Scope

* No OpenAI calls
* No embeddings or chunking logic
* No LangChain or agent setup
* No document upload or parsing
* No chat functionality
* No Vercel/Railway/Supabase deployment (that's Milestone 6)

## Directory Structure

After this milestone, the repo should look like:

```
miniglean/
├── CLAUDE.md
├── README.md
├── docker-compose.yml
├── .gitignore
├── .env.example
│
├── apps/
│   ├── web/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── theme.ts
│   │   ├── public/
│   │   ├── tailwind.config.ts
│   │   ├── tsconfig.json
│   │   ├── next.config.js
│   │   ├── package.json
│   │   └── .env.local
│   │
│   └── api/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models.py
│       ├── routers/
│       │   └── health.py
│       ├── services/
│       ├── repositories/
│       │   ├── document_repository.py
│       │   └── chunk_repository.py
│       ├── tools/
│       ├── prompts/
│       ├── alembic/
│       │   ├── env.py
│       │   ├── script.py.mako
│       │   └── versions/
│       │       └── 001_initial_schema.py
│       ├── alembic.ini
│       ├── requirements.txt
│       ├── .env
│       └── .env.example
│
├── packages/
│   └── shared/
│       ├── types.ts
│       └── package.json
│
├── docs/
│   ├── architecture.md
│   ├── database.md
│   ├── deployment.md
│   ├── environment-variables.md
│   └── integration-test.md
│
├── milestones/
│   ├── 01-setup.md
│   ├── 02-ingestion.md
│   ├── 03-rag-core.md
│   ├── 04-chat-agent.md
│   ├── 05-ui-polish.md
│   └── 06-demo-ready.md
│
└── .claude/
    └── skills/
        ├── add-api-endpoint.md
        ├── add-rag-tool.md
        ├── add-ui-component.md
        ├── add-prompt.md
        ├── write-test.md
        ├── code-review.md
        ├── code-standards.md
        ├── material-design-3.md
        ├── debug-retrieval.md
        ├── debug-agent.md
        └── deploy.md
```

## Tasks

### 1. Scaffold the monorepo

Create the top-level folder structure:

```bash
mkdir -p apps/web apps/api packages/shared docs milestones .claude/skills
```

Create root files:

* `CLAUDE.md` — project context for Claude Code
* `README.md` — setup instructions
* `docker-compose.yml` — local dev orchestration
* `.gitignore` — ignore `.env`, `node_modules`, `__pycache__`, `data/`
* `.env.example` — all env var names, no real values

### 2. Initialize the frontend (`apps/web`)

**Tech:** Next.js 14, App Router, Tailwind CSS, TypeScript strict mode

```bash
cd apps/web
npx create-next-app@latest . --app --typescript --tailwind --eslint --src-dir=false
```

Configure:

* Enable strict mode in `tsconfig.json`
* Set up MD3 color tokens in `tailwind.config.ts`
* Create `lib/theme.ts` with typography and color constants
* Create `lib/api.ts` with the base API client (points to `NEXT_PUBLIC_API_URL`)
* Create a minimal home page (`app/page.tsx`) that displays "MiniGlean" heading
* Create `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`

Verify:

* `npm run dev` starts without errors
* `http://localhost:3000` shows the home page
* `npm run lint` passes

### 3. Initialize the backend (`apps/api`)

**Tech:** FastAPI, Python 3.11, async SQLAlchemy, pgvector, pydantic-settings, Alembic

Create `requirements.txt`:

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
pgvector==0.2.4
pydantic-settings==2.1.0
alembic==1.13.1
python-multipart==0.0.6
httpx==0.26.0
ruff==0.1.14
pytest==7.4.4
pytest-asyncio==0.23.3
```

Create `config.py`:

* `Settings` class using `pydantic-settings` that:
  * Loads from `.env` file
  * Validates required vars (`OPENAI_API_KEY`, `DATABASE_URL`) at startup
  * Sets sensible defaults for optional vars
  * Fails fast with a clear error if required vars are missing

Create `database.py`:

* Async engine using `asyncpg` driver
* Async session maker
* `get_session()` dependency for FastAPI injection
* Echo SQL in development mode only

Create `models.py`:

* Base declarative class
* `Document` model with all columns
* `Chunk` model with `Vector(1536)` column
* Relationship between `Document` → `Chunks` with cascade delete

Create `main.py`:

* FastAPI app instance with title and version
* CORS middleware configured from `ALLOWED_ORIGINS` env var
* Health router included
* Startup event that verifies database connection

Create `routers/health.py`:

* `GET /health` endpoint
* Attempts a simple query (`SELECT 1`) against the database
* Returns `{ "status": "ok", "database": "connected", "environment": "..." }`
* Returns `{ "status": "degraded", "database": "disconnected", "error": "..." }` on failure

Verify:

* `uvicorn main:app --reload` starts without errors
* `http://localhost:8000/docs` shows Swagger UI
* `http://localhost:8000/health` returns a response (DB may fail until Docker is up)
* `ruff check .` passes

### 4. Create repository classes

`repositories/document_repository.py` — scaffold with methods (implementation can be minimal — just the interface):

* `create(document)` → `Document`
* `get_by_id(doc_id)` → `Document | None`
* `list_all()` → `list[Document]`
* `count()` → `int`
* `delete(doc_id)` → `bool`

`repositories/chunk_repository.py` — scaffold with methods:

* `add_chunks(chunks)` → `None`
* `search_similar(embedding, top_k)` → `list[dict]`
* `get_by_document_id(doc_id)` → `list[Chunk]`
* `delete_by_document_id(doc_id)` → `int`

### 5. Set up Alembic

```bash
cd apps/api
alembic init alembic
```

Configure `alembic.ini`:

* Set `sqlalchemy.url` to use `DATABASE_URL` from environment

Configure `alembic/env.py`:

* Import `Base` from `models.py` for autogenerate support
* Use async engine

Create initial migration `001_initial_schema.py`:

* Enable pgvector extension
* Create `documents` table with all columns and indexes
* Create `chunks` table with vector column and indexes
* Create IVFFlat vector similarity index

Verify:

* `alembic upgrade head` runs without errors (requires running Postgres)
* `alembic current` shows the applied migration
* Tables exist in the database

### 6. Set up Docker Compose

```yaml
# docker-compose.yml
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: miniglean
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./apps/api:/app
    env_file:
      - ./apps/api/.env
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  web:
    build:
      context: .
      dockerfile: apps/web/Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./apps/web:/app
      - /app/node_modules
    env_file:
      - ./apps/web/.env.local
    depends_on:
      - api
    command: npm run dev

volumes:
  pgdata:
```

Create `apps/api/Dockerfile.dev`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/api/ .
```

Create `apps/web/Dockerfile.dev`:

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY apps/web/package*.json .
RUN npm install
COPY apps/web/ .
```

Verify:

* `docker-compose up` starts all three services
* Database is healthy before API starts
* API can connect to database
* Frontend can reach API

### 7. Create shared types package

`packages/shared/types.ts`:

```typescript
export interface Document {
  id: string
  filename: string
  type: 'pdf' | 'url' | 'note'
  tags: string[]
  chunk_count: number
  created_at: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources: SourceCitation[]
  created_at: string
}

export interface SourceCitation {
  doc_id: string
  filename: string
  excerpt: string
}

export interface HealthResponse {
  status: 'ok' | 'degraded'
  database: 'connected' | 'disconnected'
  environment: string
  error?: string
}
```

`packages/shared/package.json`:

```json
{
  "name": "@miniglean/shared",
  "version": "0.1.0",
  "main": "types.ts",
  "types": "types.ts"
}
```

### 8. Create `.gitignore`

```
# Environment
.env
.env.local
!.env.example

# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# Node
node_modules/
.next/

# Data
data/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db
```

### 9. Create `.env.example`

```bash
# apps/api/.env.example
OPENAI_API_KEY=
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/miniglean
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
MAX_DOCUMENTS=20
CHUNK_SIZE=500
CHUNK_OVERLAP=50
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.0
TOP_K_RESULTS=5
LOG_LEVEL=DEBUG
```

```bash
# apps/web/.env.example
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 10. Write the README

Include:

* One-line project description
* Tech stack table
* Prerequisites (Docker, Node 20, Python 3.11)
* Quick start (`docker-compose up`)
* Manual start (each service individually)
* Link to `docs/` for architecture and deployment details

## Verification Steps

After completing all tasks, run through this sequence:

```bash
# 1. Start everything
docker-compose up

# 2. Wait for all services to be healthy (~30 seconds)

# 3. Check database
docker-compose exec db psql -U postgres -d miniglean -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
# Should show vector extension

# 4. Run migration
docker-compose exec api alembic upgrade head

# 5. Verify tables exist
docker-compose exec db psql -U postgres -d miniglean -c "\dt"
# Should show: documents, chunks, alembic_version

# 6. Check health endpoint
curl http://localhost:8000/health
# Should return: { "status": "ok", "database": "connected", "environment": "development" }

# 7. Check API docs
open http://localhost:8000/docs
# Should show Swagger UI with /health endpoint

# 8. Check frontend
open http://localhost:3000
# Should show MiniGlean home page

# 9. Lint backend
cd apps/api && ruff check .
# Should pass with zero warnings

# 10. Lint frontend
cd apps/web && npm run lint
# Should pass with zero errors
```

## Decisions Made in This Milestone

| Decision | Choice | Reason |
|---|---|---|
| Async SQLAlchemy | Yes | FastAPI is async — blocking DB calls would waste concurrency |
| asyncpg driver | Over psycopg2 | Native async, better performance with async SQLAlchemy |
| pgvector Docker image | `pgvector/pgvector:pg16` | Includes pgvector pre-installed, matches Supabase Postgres version |
| Repository pattern | Yes | Clean separation — services don't know about SQL |
| Alembic for migrations | Yes | Standard, version-controlled, supports async |
| pydantic-settings | Yes | Type-safe config, validates at startup, loads `.env` |
| Separate Dockerfiles for dev | Yes | Hot reload with volume mounts — faster dev cycle |
| Shared types package | Yes | Single source of truth for frontend/backend contracts |

## What's Next

After this milestone is complete, move to **Milestone 2 — Document Ingestion** where we'll add:

* PDF parsing (`pdfplumber`)
* URL scraping (`BeautifulSoup`)
* Text chunking
* OpenAI embedding calls
* Storing chunks with vectors in the database
* Upload, list, and delete endpoints
