# MiniGlean

A personal knowledge base with AI-powered search and chat

MiniGlean lets you upload PDFs, save URLs, and create notes, then search and chat with your knowledge using AI. Every answer is grounded in your documents and comes back with source citations.

> ![MiniGlean demo](docs/assets/demo.gif)
> _Demo GIF placeholder — record a ~20s walkthrough following [demo/demo-script.md](demo/demo-script.md) and save it to `docs/assets/demo.gif`._

## Features

- **Ingest anything** — upload PDFs, scrape static web pages by URL, or jot quick notes with tags.
- **RAG search** — documents are chunked, embedded, and stored as vectors; questions run a cosine-similarity search over them.
- **Agentic chat** — a LangChain agent with four tools (search, summarize, compare, add-note) chooses how to answer.
- **Streaming answers** — responses stream token by token over Server-Sent Events.
- **Always cited** — every AI answer includes the source documents it used.
- **Graceful failure** — friendly, specific messages for offline state, rate limits, parse failures, and dropped streams, with retry.

## Tech Stack

| Layer | Technology | Hosted On |
|-------|-----------|-----------|
| Frontend | Next.js (App Router), React 19, TypeScript, Tailwind CSS v4, Material Design 3 | AWS Amplify |
| Backend | FastAPI, Python 3.11, Async SQLAlchemy, Pydantic, Mangum | AWS Lambda + API Gateway |
| AI / Agent | LangChain, OpenAI GPT-4o, text-embedding-3-small | OpenAI API |
| Database | PostgreSQL 16 with pgvector | AWS RDS |
| Infrastructure | AWS CDK (TypeScript) | — |
| Migrations | Alembic | — |
| Local dev | Docker Compose | — |

## Prerequisites

- Docker Desktop
- Node.js 20+
- Python 3.11+ (optional, for local development without Docker)
- OpenAI API key

## Quick Start

1. **Clone and navigate to the repository**

```bash
cd miniglean
```

2. **Set up environment variables**

```bash
# Create .env file for the API
cp apps/api/.env.example apps/api/.env
# Edit apps/api/.env and add your OPENAI_API_KEY
```

3. **Start all services with Docker Compose**

```bash
docker-compose up
```

This will start:
- PostgreSQL with pgvector at `localhost:5432`
- FastAPI backend at `http://localhost:8000`
- Next.js frontend at `http://localhost:3000`

4. **Run database migrations** (in a new terminal)

```bash
docker-compose exec api alembic upgrade head
```

5. **Verify everything is running**

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

6. **Seed demo data** (optional, in a new terminal)

Generate the sample PDFs and load them, plus a meeting note, into the running app. The seed is idempotent — safe to run more than once.

```bash
# Generate the demo PDFs (one-time)
cd apps/api && .venv/bin/python ../../demo/generate_documents.py

# Load them into the running app
cd ../.. && NEXT_PUBLIC_API_URL=http://localhost:8000 npx tsx demo/seed.ts
```

## Manual Start (without Docker)

### Database

```bash
# Start PostgreSQL with pgvector (requires Docker)
docker-compose up db
```

### Backend

```bash
cd apps/api

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start API server
uvicorn main:app --reload
```

### Frontend

```bash
cd apps/web

# Install dependencies
npm install

# Start dev server
npm run dev
```

## Project Structure

```
miniglean/
├── apps/
│   ├── api/          # FastAPI backend
│   │   ├── alembic/  # Database migrations
│   │   ├── models.py # SQLAlchemy models
│   │   ├── repositories/ # Data access layer
│   │   ├── services/ # Business logic
│   │   ├── routers/  # API endpoints
│   │   └── main.py   # FastAPI app
│   └── web/          # Next.js frontend
│       ├── app/      # App Router pages
│       ├── components/ # React components
│       └── lib/      # Utilities (API client, theme)
├── packages/
│   └── shared/       # Shared TypeScript types
├── infra/            # AWS CDK infrastructure (Lambda, RDS, Amplify)
│   ├── bin/          # CDK app entry point
│   └── stacks/       # Database, secrets, API, frontend constructs
├── demo/             # Demo seed script and sample documents
├── docs/             # Documentation
└── docker-compose.yml
```

## Development

### Linting

```bash
# Frontend
cd apps/web && npm run lint

# Backend
cd apps/api && ruff check .
```

### Database Migrations

```bash
cd apps/api

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Documentation

See the `docs/` directory for detailed documentation:

- [Architecture](docs/architecture.md)
- [Database Schema](docs/database.md)
- [Environment Variables](docs/environment-variables.md)
- [Deployment](docs/deployment.md)
- [Integration Testing](docs/integration-test.md)
- [Contributing](CONTRIBUTING.md)
- [Demo Script](demo/demo-script.md)

## Milestones

Development is tracked through milestones in the `milestones/` directory:

1. ✅ Project Setup (infrastructure, database, Docker)
2. ✅ Document Ingestion (PDF parsing, URL scraping, chunking)
3. ✅ RAG Core (embeddings, vector search)
4. ✅ Chat Agent (LangChain, OpenAI)
5. ✅ UI Polish (Material Design 3 components)
6. ✅ Demo Ready (AWS infra, CI/CD, hardening, seed)

## License

MIT
