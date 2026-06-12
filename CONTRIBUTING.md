# Contributing to MiniGlean

Thanks for your interest in MiniGlean. This is a single-user portfolio project,
but the workflow below keeps the codebase clean and reviewable.

## Getting set up

See the [README](README.md) Quick Start for running the app with Docker
Compose, or the Manual Start section for running the backend and frontend
directly.

## Project conventions

- **Backend** lives in `apps/api` (FastAPI). Routes go in `routers/`, business
  logic in `services/`, data access in `repositories/`, agent tools in
  `tools/`, and prompts in `prompts/`. Never write raw SQL in a router — go
  through a repository. Never call OpenAI directly — go through `services/`.
- **Frontend** lives in `apps/web` (Next.js App Router). Components in
  `components/`, hooks in `hooks/`, and the single API client in `lib/api.ts`.
  No component should call `fetch` directly.
- **Shared types** live in `packages/shared`.
- **Infrastructure** is in `infra/` (AWS CDK). All AWS resources are defined in
  code — no manual console changes.
- Embeddings always use `text-embedding-3-small` (1536 dims). Chunk size is 500
  tokens with 50 overlap.
- Every AI answer must return source citations.

## Branching

- Branch off `dev` for day-to-day work.
- Use descriptive branch names: `feat/streaming-chat`, `fix/upload-reset`,
  `docs/deployment`, `chore/ci-gate`.
- Open PRs against `main`. `main` is what deploys.

## Commit messages

Use short, imperative subjects, optionally prefixed by type:

```
feat: add retry button to chat error banner
fix: reset file input after a failed upload
docs: document AWS deployment steps
chore: gate deploy workflow on CI
```

Squash work-in-progress commits before merging so history stays meaningful.

## Pre-push checklist

Run these locally before pushing. They mirror the CI workflow
(`.github/workflows/test.yml`), which must pass before `main` deploys.

**Backend** (`apps/api`):

```bash
.venv/bin/ruff check .
.venv/bin/python -m pytest tests/unit/
```

**Frontend** (`apps/web`):

```bash
npm run lint
npx tsc --noEmit
```

**Infrastructure** (`infra`), if you changed it:

```bash
npx tsc --noEmit
npx cdk synth
```

## Database changes

Schema changes go through Alembic — never run `CREATE TABLE` or similar from
application code.

```bash
cd apps/api
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

## Secrets

Never commit secrets. Only `.env.example` is tracked; `.env` is gitignored. In
production, secrets live in AWS SSM Parameter Store as SecureStrings (see
[docs/deployment.md](docs/deployment.md)).
