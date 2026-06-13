# Portfolio Quickstart

Get MiniGlean running in under 3 minutes for portfolio screenshots/demos.

> **🎭 No API key? Use [Mock Mode](MOCK_MODE.md)** - runs completely offline with pre-loaded data!

## Prerequisites

- Docker Desktop (running)
- OpenAI API key (get free $5 credits at platform.openai.com/api-keys)

## Automated Setup (Recommended)

Run the setup script:

```bash
./portfolio-setup.sh
```

The script will:
1. Check prerequisites
2. Set up your .env file (prompts for API key if needed)
3. Start all services with Docker
4. Run database migrations
5. Seed 3 demo documents

Then open http://localhost:3000 and try the demo questions!

## Manual Setup

If you prefer to run each step manually:

1. **Set up your API key**

```bash
# Create the .env file
cp apps/api/.env.example apps/api/.env
```

Edit `apps/api/.env` and add your OpenAI key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

2. **Start everything**

```bash
docker-compose up -d
```

3. **Run migrations**

```bash
docker-compose exec api alembic upgrade head
```

4. **Seed demo data**

```bash
cd demo
npm install tsx
NEXT_PUBLIC_API_URL=http://localhost:8000 npx tsx seed.ts
```

5. **Open and test**

- Go to http://localhost:3000
- Try asking: **"How much notice do I need to give to end my lease?"**
- Or: **"What are the action items from the team meeting?"**

## Taking Screenshots

The demo script in `demo/demo-script.md` has a full 3-minute walkthrough optimized for recording.

## Shutting Down

```bash
docker-compose down        # Stop services
docker-compose down -v     # Stop + delete database (fresh start next time)
```

## Cost Note

This uses real OpenAI API calls:
- Embeddings: ~$0.0001 per document  
- Chat: ~$0.001 per question
- Full demo: < $0.10 total

You can delete all data afterward and the cost stays minimal.
