# MiniGlean

> A personal knowledge base with AI-powered search and chat

MiniGlean lets you upload PDFs, save URLs, and create notes, then search and chat with your knowledge using AI.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 19, TypeScript, Tailwind CSS (v4), Material Design 3 |
| Backend | FastAPI, Python 3.11, Async SQLAlchemy, Pydantic |
| Database | PostgreSQL 16 with pgvector extension |
| AI | OpenAI (GPT-4o, text-embedding-3-small) |
| Orchestration | Docker Compose |
| Migrations | Alembic |

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

## Milestones

Development is tracked through milestones in the `milestones/` directory:

1. ✅ Project Setup (infrastructure, database, Docker)
2. Document Ingestion (PDF parsing, URL scraping, chunking)
3. RAG Core (embeddings, vector search)
4. Chat Agent (LangChain, OpenAI)
5. UI Polish (Material Design 3 components)
6. Demo Ready (deployment, testing)

## License

MIT
