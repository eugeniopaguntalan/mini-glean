# Skill: Deploy

## When to Use
- Deploying a new version to production
- Adding a new environment variable
- Running database migrations
- Debugging a deployment failure
- Setting up a new environment

---

## Architecture

| Component | Platform | URL Pattern |
|---|---|---|
| Frontend | Vercel | `https://miniglean.vercel.app` |
| Backend | Railway | `https://miniglean.railway.app` |
| Database | Supabase | `https://xxx.supabase.co` |

---

## Deploy Flow

```text
Push to main
├── Vercel auto-deploys frontend
└── Railway auto-deploys backend
└── Run alembic upgrade head (if schema changed)

```

---

## Deploy Steps

### Backend (Railway)

1. Push to `main` → Railway auto-deploys
2. If schema changed → open Railway shell → run `alembic upgrade head`
3. Verify: `curl https://your-app.railway.app/health`
4. Expected: `{ "status": "ok", "database": "connected" }`

### Frontend (Vercel)

1. Push to `main` → Vercel auto-deploys
2. If API URL changed → update `NEXT_PUBLIC_API_URL` in Vercel dashboard
3. Verify: visit the app, upload a document, ask a question

### Database (Supabase)

1. Write migration locally: `alembic revision --autogenerate -m "description"`
2. Test locally: `alembic upgrade head` against local Postgres
3. Apply to prod: run `alembic upgrade head` from Railway shell after backend deploys

---

## Adding an Environment Variable

1. Add to `apps/api/config.py` Settings class with a sensible default
2. Add to `.env.example` (no real value — just the key name)
3. Add to `.env` locally for development
4. Set in Railway dashboard (backend vars)
5. Set in Vercel dashboard (frontend vars — must have `NEXT_PUBLIC_` prefix)
6. Redeploy for changes to take effect

---

## First-Time Setup

### Supabase

1. Create project at https://supabase.com → New project
2. Name: `miniglean`, region: closest to you
3. Enable pgvector: run `CREATE EXTENSION IF NOT EXISTS vector;` in SQL Editor
4. Copy connection string from Settings → Database → URI
5. Save project URL and anon key

### Railway

1. Go to https://railway.app → New project → Deploy from GitHub
2. Set root directory: `apps/api`
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (see below)
6. Open shell → run `alembic upgrade head`

### Vercel

1. Go to https://vercel.com → Import Git Repository
2. Set root directory: `apps/web`
3. Framework preset: Next.js
4. Add `NEXT_PUBLIC_API_URL` pointing to Railway URL

---

## Environment Variables by Platform

### Railway

```text
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=postgresql://user:pass@host:5432/postgres
ENVIRONMENT=production
ALLOWED_ORIGINS=https://miniglean.vercel.app
MAX_DOCUMENTS=20
LOG_LEVEL=INFO
```

### Vercel

```text
NEXT_PUBLIC_API_URL=https://miniglean.railway.app
```

### Supabase

No env vars to set — it's the database. You configure access via `DATABASE_URL` on Railway.

---

## CORS Configuration

Backend must allow the Vercel frontend origin.

```text
ALLOWED_ORIGINS=https://miniglean.vercel.app
```

For multiple origins (e.g. preview deploys):

```text
ALLOWED_ORIGINS=https://miniglean.vercel.app,https://miniglean-git-feat-xyz.vercel.app
```

---

## Database Migrations

### Create a migration

```bash
cd apps/api
alembic revision --autogenerate -m "add tags column to documents"

```

## Apply locally

```text
alembic upgrade head
```

## Apply to production

```text
# Open Railway shell
alembic upgrade head
```

## Rollback

```text
# One step back
alembic downgrade -1

# Check current version
alembic current

# See migration history
alembic history
```

## Migration Rules
- Always test locally before applying to production
- Never edit a migration that's already been applied to production
- One migration per logical change
- Verify with alembic current after applying

### Rollback

| Service | How |
|---------|-----|
| Railway | Dashboard → Deployments → Redeploy previous |
| Vercel | Dashboard → Deployments → Promote previous to production |
| Database | `alembic downgrade -1` from Railway shell |

## Health Check

```The /health endpoint verifies backend + database connectivity.```

```bash
curl https://your-app.railway.app/health
Expected response:
```

```json
json
{
  "status": "ok",
  "database": "connected",
  "environment": "production"
}
```

If database is unreachable:

```json
json
{
  "status": "degraded",
  "database": "disconnected",
  "error": "connection refused"
}
```

### Debugging Failed Deploys

#### Railway — Build Fails

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError` | Missing dependency | Add to `requirements.txt` |
| `ImportError` | Wrong Python version | Check `runtime.txt` or `Dockerfile` |
| Build timeout | Too many dependencies | Use a multi-stage Dockerfile |

#### Railway — Runtime Fails

| Symptom | Cause | Fix |
|---------|-------|-----|
| Connection refused (DB) | Wrong `DATABASE_URL` | Check Supabase connection string |
| Invalid API key | Missing or wrong `OPENAI_API_KEY` | Re-set in Railway vars |
| Port mismatch | Hardcoded port | Use `$PORT` env var |

#### Vercel — Build Fails

| Symptom | Cause | Fix |
|---------|-------|-----|
| TypeScript errors | Strict mode violations | Fix type errors locally first |
| Missing env var | `NEXT_PUBLIC_` not set | Add to Vercel dashboard |
| Build timeout | Large dependencies | Check bundle size |

#### Supabase — Connection Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `FATAL: password authentication failed` | Wrong credentials in URL | Re-copy from Supabase dashboard |
| `relation does not exist` | Migration not applied | Run `alembic upgrade head` |
| `type "vector" does not exist` | pgvector not enabled | Run `CREATE EXTENSION vector;` |

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cost (Free Tier Limits)

| Service | Free Tier | Watch Out For |
|---------|-----------|---------------|
| Vercel | 100GB bandwidth/month | Preview deploys count toward bandwidth |
| Railway | $5 credit/month | ~500 hours runtime — sleeps after inactivity |
| Supabase | 500MB DB, 2GB bandwidth | Pauses after 1 week inactivity on free tier |
| OpenAI | Pay-as-you-go | ~$0.01 per query — no free tier

## Keeping Free Tier Active
- Railway: will sleep after inactivity — first request after sleep is slow (~10s cold start)
- Supabase: pauses after 7 days inactivity — set up a weekly cron ping or use the dashboard periodically
- Vercel: no sleep — always available

## Smoke Test (After Every Deploy)
Run this manually after deploying:
- Visit frontend URL — page loads
- Upload a small test PDF — returns 201
- Check document library — new doc appears
- Ask a question about the PDF — get a cited answer
- Delete the test document — returns 204
- Confirm it's gone from the library

## Rules
- Never deploy database migrations without testing locally first
- Always verify /health after backend deploy
- Always run smoke test after frontend deploy
- Don't add env vars only to local .env — add to platform dashboards too
- Railway auto-deploys on push to main — be careful what you merge
- Don't store secrets in code or commit .env
- If Supabase pauses, re-activate from dashboard before deploying migrations

## Checklist (Every Deploy)
- All tests pass locally (pytest + npm test)
- No new env vars missing from platform dashboards
- Database migration applied (if schema changed)
- GET /health returns 200 with database: connected
- Frontend loads and can reach backend
- Smoke test passed: upload → ask → get cited answer
- No secrets exposed in client-side code
- CORS allows the current Vercel domain