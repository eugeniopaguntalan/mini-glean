# MiniGlean

Personal AI knowledge search assistant. Upload docs, paste URLs, write notes — then search and chat across all of it.

## Stack
| Layer | Tech | Hosted On |
|---|---|---|
| Frontend | Next.js 14 (App Router) + Tailwind | Vercel |
| Backend | FastAPI + Python 3.11 | Railway |
| Database | Postgres + pgvector | Supabase (free tier) |
| AI | LangChain + OpenAI `gpt-4o` + `text-embedding-3-small` | OpenAI API |
| Monorepo | npm workspaces (frontend) + single Python venv (backend) | — |

## Monorepo Layout

```text
apps/web/        → Next.js frontend (deployed to Vercel)
apps/api/        → FastAPI backend (deployed to Railway)
packages/shared/ → Shared TS types
docs/            → Architecture, deployment, testing docs
milestones/      → Chunked delivery plans
.claude/skills/  → Reusable task playbooks
```

## Dev Commands
```bash
# Start everything locally
docker-compose up

# Frontend only
cd apps/web && npm run dev

# Backend only
cd apps/api && uvicorn main:app --reload

# Run unit tests
cd apps/api && pytest
cd apps/web && npm test

# Run integration tests
cd apps/api && pytest tests/integration/ --env=staging

# Lint
cd apps/api && ruff check .
cd apps/web && npm run lint

# Database migrations
cd apps/api && alembic upgrade head
```

## Architecture — RAG Pipeline

Upload (PDF / URL / text)
  → Parse & chunk (500 tokens, 50 overlap)
  → Embed (text-embedding-3-small)
  → Store chunks + embeddings in Supabase (pgvector)
  → Store document metadata in same DB

User question
  → Agent decides: search | summarize | compare | clarify
  → Vector similarity search via pgvector (cosine distance)
  → Retrieve top-5 chunks
  → GPT-4o generates answer + cites source doc IDs
  → Return answer + sources to frontend
  
### Database
Single Supabase Postgres instance with pgvector extension.
- documents table → metadata (id, filename, type, tags, chunk_count, created_at)
- chunks table → content + embedding vector (1536 dimensions)
- Vector search uses cosine distance operator <=>
- See docs/database.md for full schema

### Key Conventions
#### Backend
- All routes in apps/api/routers/
- Business logic in apps/api/services/
- RAG tools in apps/api/tools/
- Prompts in apps/api/prompts/
- DB access through apps/api/repositories/ — never raw SQL in services
- Never call OpenAI directly — always through services/llm.py
- Database migrations via Alembic

#### Frontend
- Pages in app/ (App Router only)
- Reusable components in components/
- API calls in lib/api.ts
- Types from packages/shared/types.ts

#### General

- Chunk size: 500 tokens, overlap: 50
- Embedding model: text-embedding-3-small (1536 dimensions)
- Always return source citations with every AI answer
- Every AI response includes source_doc_ids

### What NOT to Do
- Don't add auth — single-user app
- Don't query the database directly in routers — use repositories
- Don't mix embedding models — always text-embedding-3-small
- Don't use pages/ router in Next.js — App Router only
- Don't exceed 20 documents for demo stability
- Don't scrape JS-heavy sites — static HTML only
- Don't commit .env — only .env.example
- Don't run migrations in application code — use Alembic CLI

### Environment Variables
See docs/environment-variables.md for full reference.

```bash
# Required (backend)
OPENAI_API_KEY=
DATABASE_URL=

# Required (frontend)
NEXT_PUBLIC_API_URL=
```

### Deployment

| Component | Platform | Deploys On |
|-----------|----------|------------|
| Frontend | Vercel | Push to main |
| Backend | Railway | Push to main |
| Database | Supabase | Alembic migrations |

*See docs/deployment.md for full instructions.*

### Skills Reference

| Skill | When to Use |
|-------|-------------|
| add-api-endpoint | Adding a FastAPI route |
| add-rag-tool | Adding a new agent tool |
| add-ui-component | Adding a React component |
| add-prompt | Writing an LLM prompt |
| write-test | Writing backend or frontend tests |
| code-review | Reviewing any PR |
| code-standards | Naming, structure, style |
| material-design-3 | Building or styling UI |
| debug-retrieval | RAG returning bad results |
| debug-agent | Agent picking wrong tools |
| deploy | Deploying to Vercel / Railway / Supabase |

### Documentation

| Doc | Content |
|-----|---------|
| docs/architecture.md | System design, data flows, tech decisions |
| docs/deployment.md | Deploy instructions for all platforms |
| docs/database.md | Schema, pgvector, Alembic, repositories |
| docs/environment-variables.md | Env var reference for all environments |
| docs/integration-test.md | Integration test scenarios and setup |

### Current Milestone

*See `milestones/` — start with `01-setup.md`*


