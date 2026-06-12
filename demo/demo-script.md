# MiniGlean — 3-Minute Demo Script

A tight, honest walkthrough of what MiniGlean does and how it's built. Times are
guides, not gospel.

> **Setup (before recording):** start the app (`docker-compose up`), then seed
> the knowledge base with `NEXT_PUBLIC_API_URL=http://localhost:8000 npx tsx demo/seed.ts`.
> This loads a rental contract (PDF), FastAPI study notes (PDF), and a team
> meeting note (text).

---

## 0:00 — The pitch (20s)

> "MiniGlean is a personal knowledge search assistant. You drop in documents —
> PDFs, web pages, or quick notes — and then ask questions across all of them in
> plain English. Every answer comes back with citations to the source document,
> so you can trust it."

## 0:20 — Add a document (30s)

- Open the app. Point out the three ingest tabs: **PDF**, **URL**, **Note**.
- Drag a PDF onto the upload zone (or show the already-seeded library).
- Mention: "On upload, the backend parses the file, splits it into ~500-token
  chunks, embeds each chunk with OpenAI's `text-embedding-3-small`, and stores
  the vectors in Postgres using the pgvector extension."

## 0:50 — Ask a question (40s)

- Type: **"How much notice do I need to give to end my lease?"**
- The answer streams in token by token.
- Call out the **source citation** under the answer pointing to
  `rental-contract.pdf`.
- "The answer is grounded in my documents — it pulled the 30-day notice clause
  straight from the contract, not from the model's general knowledge."

## 1:30 — Cross-document + the agent (45s)

- Ask: **"What are the action items from the team meeting and when are they
  due?"**
- "Behind the scenes there's a LangChain agent with four tools — search,
  summarize, compare, and add-note. It decides which tool fits the question.
  Here it searched the meeting note and pulled out the action items with dates."
- Optionally ask a comparison: **"Compare the rental contract and the FastAPI
  notes."** to show the compare tool.

## 2:15 — Resilience (25s)

- "It's built to fail gracefully." Show one of:
  - Stop the backend, send a message → friendly banner with a **Retry** button.
  - Upload a non-PDF → clear, specific error and the file input resets.
- "Rate limits, parse failures, offline state, and disconnected streams all get
  human-readable messages instead of a stack trace."

## 2:40 — The stack & wrap (20s)

> "Frontend is Next.js with Tailwind and a Material Design 3 look, deployed on
> AWS Amplify. The backend is FastAPI on Lambda, behind an HTTP API. Data lives
> in RDS Postgres with pgvector. Everything — network, database, Lambda, and
> frontend — is defined in AWS CDK, and a CI pipeline gates deploys so nothing
> ships unless the tests pass."

> "That's MiniGlean: upload anything, ask anything, get cited answers."

---

## Talking points / FAQ

- **Why an agent and not just RAG?** The agent can choose to summarize or
  compare instead of doing a raw similarity search, which handles broader
  questions better.
- **Why cap at 20 documents?** It's a single-user demo app; the cap keeps
  retrieval fast and predictable.
- **Where are the secrets?** In SSM Parameter Store as SecureStrings — nothing
  sensitive is in the repo or in Lambda's environment config.
