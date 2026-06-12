# Architecture

## Overview

MiniGlean is a personal AI knowledge search assistant. Users upload documents, paste URLs, or write notes — then search and chat across all of it using a RAG-powered agent.

The system is deployed across three cloud services on free tiers: Vercel (frontend), Railway (backend), and Supabase (database with vector search).

---

## System Diagram

```mermaid
graph TB
    subgraph Vercel
        UI[Next.js 14<br/>App Router + Tailwind + MD3]
    end

    subgraph Railway
        API[FastAPI]
        API --> Routers[Routers]
        API --> Services[Services]
        API --> Repositories[Repositories]
        API --> Tools[Agent Tools]
        API --> Prompts[Prompts]
    end

    subgraph Supabase
        DB[(Postgres + pgvector)]
        DB --> Documents[documents table]
        DB --> Chunks[chunks table<br/>+ vector index]
    end

    subgraph OpenAI
        GPT[gpt-4o]
        Embed[text-embedding-3-small]
    end

    UI -->|HTTPS JSON| API
    Repositories -->|SQL + pgvector| DB
    Services -->|API| GPT
    Services -->|API| Embed
```

## Layer Architecture

```mermaid
graph LR
    subgraph Frontend
        Pages[Pages] --> Components[Components]
        Components --> Hooks[Hooks]
        Hooks --> ApiClient[lib/api.ts]
    end

    subgraph Backend
        Router[Router] --> Service[Service]
        Service --> Repo[Repository]
        Service --> LLM[LLM Service]
        Service --> Tool[Tools]
        Tool --> Repo
        Tool --> LLM
    end

    subgraph Database
        Postgres[(Postgres)]
        PGVector[(pgvector)]
    end

    ApiClient -->|HTTP| Router
    Repo -->|SQL| Postgres
    Repo -->|Vector Search| PGVector
    LLM -->|API| OpenAI[OpenAI API]
```

## Backend Layer Responsibilities

```mermaid
graph TD
    Request[HTTP Request] --> Router

    Router -->|Parse request<br/>Map exceptions to HTTP| Service
    Service -->|Business logic<br/>Orchestration| Repository
    Service -->|LLM calls| LLMService[services/llm.py]
    Repository -->|SQL queries<br/>Vector search| DB[(Supabase)]
    LLMService -->|API calls| OpenAI[OpenAI]

    Router -->|Response| Client[HTTP Response]

    style Router fill:#e3f2fd
    style Service fill:#f3e5f5
    style Repository fill:#e8f5e9
    style LLMService fill:#fff3e0
```

| Layer | Location | Responsibility | Allowed to Call |
|-------|----------|----------------|-----------------|
| Router | `routers/` | HTTP parsing, status codes, CORS | Services only |
| Service | `services/` | Business logic, orchestration | Repositories, LLM service |
| Repository | `repositories/` | SQL queries, vector search, returns data | Database only |
| Tool | `tools/` | Agent capabilities | Repositories, LLM service |
| Prompt | `prompts/` | LLM prompt templates | Nothing — these are constants |

## Data Flow — Document Ingestion

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Router
    participant Service
    participant Embedder
    participant Repository
    participant Supabase

    User->>Frontend: Upload PDF / Paste URL / Write note
    Frontend->>Router: POST /documents/upload
    Router->>Service: ingest(request)
    Service->>Service: Parse content (pdfplumber / BeautifulSoup / raw)
    Service->>Service: Chunk text (500 tokens, 50 overlap)
    Service->>Embedder: embed_chunks(chunks)
    Embedder->>OpenAI: text-embedding-3-small
    OpenAI-->>Embedder: 1536-dim vectors
    Embedder-->>Service: embeddings[]
    Service->>Repository: create_document(metadata)
    Repository->>Supabase: INSERT INTO documents
    Service->>Repository: add_chunks(chunks + embeddings)
    Repository->>Supabase: INSERT INTO chunks (with VECTOR)
    Supabase-->>Repository: OK
    Repository-->>Service: document
    Service-->>Router: DocumentResponse
    Router-->>Frontend: 201 Created
    Frontend-->>User: Document appears in library
```

## Data Flow — Chat / RAG Query

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Router
    participant Agent
    participant Tool
    participant Repository
    participant Supabase
    participant LLM

    User->>Frontend: Ask a question
    Frontend->>Router: POST /chat { question, session_id }
    Router->>Agent: invoke(question, history)
    Agent->>Agent: Read tool docstrings
    Agent->>Agent: Decide which tool to call

    alt Search tool selected
        Agent->>Tool: search_knowledge_base(query)
        Tool->>Repository: search_similar(embedding, top_k=5)
        Repository->>Supabase: SELECT ... ORDER BY embedding <=> query LIMIT 5
        Supabase-->>Repository: top-5 chunks
        Repository-->>Tool: chunks[]
        Tool-->>Agent: formatted chunks with [source: doc_id]
    end

    Agent->>LLM: Generate answer from context
    LLM->>OpenAI: gpt-4o (temperature=0.0)
    OpenAI-->>LLM: grounded answer
    LLM-->>Agent: answer + source_doc_ids
    Agent-->>Router: ChatResponse
    Router-->>Frontend: { content, sources[] }
    Frontend-->>User: Answer + citation chips
```

## Data Flow — Agent Tool Selection

```mermaid
flowchart TD
    Q[User Question] --> Agent{Agent Decision}

    Agent -->|"What does my doc say about X?"| Search[search_knowledge_base]
    Agent -->|"Summarize my notes"| Summarize[summarize_document]
    Agent -->|"Compare A and B"| Compare[compare_documents]
    Agent -->|"Remember this / Save this"| AddNote[add_note]

    Search --> VectorSearch[pgvector similarity search]
    Summarize --> GetChunks[Get all chunks for doc] --> LLMSummarize[LLM summarize]
    Compare --> GetChunksA[Get chunks doc A] --> LLMCompare[LLM compare]
    Compare --> GetChunksB[Get chunks doc B] --> LLMCompare
    AddNote --> Chunk[Chunk + Embed] --> Store[Store in DB]

    VectorSearch --> Format[Format with source IDs]
    LLMSummarize --> Format
    LLMCompare --> Format
    Store --> Confirm[Confirmation message]

    Format --> Response[Agent generates final answer]
    Confirm --> Response
```

## Database Schema

```mermaid
erDiagram
    DOCUMENTS {
        uuid id PK
        varchar filename
        varchar type
        text[] tags
        int chunk_count
        timestamptz created_at
    }

    CHUNKS {
        uuid id PK
        uuid document_id FK
        text content
        vector(1536) embedding
        int chunk_index
        timestamptz created_at
    }

    DOCUMENTS ||--o{ CHUNKS : "has many (CASCADE)"
```

## Vector Search Strategy
- Index type: IVFFlat (approximate nearest neighbour)
- Distance metric: Cosine (<=> operator)
- Index config: lists = 10 (appropriate for < 10,000 chunks)
- Dimensions: 1536 (text-embedding-3-small output)

## Frontend Architecture

```mermaid
graph TD
    subgraph Pages["App Router (Server Components)"]
        Home["/ (Home Page)"]
        Chat["/chat (Chat Page)"]
    end

    subgraph ClientComponents["Client Components"]
        UploadPanel[UploadPanel]
        DocumentLibrary[DocumentLibrary]
        ChatThread[ChatThread]
    end

    subgraph DumbComponents["Display Components"]
        DocumentCard[DocumentCard]
        ChatMessage[ChatMessage]
        SourceCitation[SourceCitation]
        TypeBadge[TypeBadge]
    end

    subgraph DataLayer["Data Layer"]
        useDocuments[useDocuments hook]
        useChat[useChat hook]
        ApiClient[lib/api.ts]
    end

    Home --> UploadPanel
    Home --> DocumentLibrary
    Chat --> ChatThread

    DocumentLibrary --> DocumentCard
    DocumentCard --> TypeBadge
    ChatThread --> ChatMessage
    ChatMessage --> SourceCitation

    UploadPanel --> ApiClient
    useDocuments --> ApiClient
    useChat --> ApiClient
    DocumentLibrary --> useDocuments
    ChatThread --> useChat

    ApiClient -->|HTTPS| Backend[Railway API]
```

## Agent Architecture

```mermaid
graph TD
    subgraph AgentCore["LangChain Agent"]
        SystemPrompt[System Prompt]
        Memory[ConversationBufferWindowMemory<br/>k=6]
        ToolSelector[Tool Selection via Docstrings]
    end

    subgraph RegisteredTools["Registered Tools"]
        T1[search_knowledge_base]
        T2[summarize_document]
        T3[compare_documents]
        T4[add_note]
    end

    subgraph Config["Agent Config"]
        Model["Model: gpt-4o"]
        Temp["Temperature: 0.0"]
        MaxIter["Max Iterations: 5"]
        ParseErr["handle_parsing_errors: true"]
    end

    Input[User Question + History] --> AgentCore
    AgentCore --> ToolSelector
    ToolSelector --> T1
    ToolSelector --> T2
    ToolSelector --> T3
    ToolSelector --> T4
    T1 --> Output[Final Answer + Sources]
    T2 --> Output
    T3 --> Output
    T4 --> Output
```

## Deployment Architecture

```mermaid
graph LR
    subgraph GitHub
        Repo[main branch]
    end

    subgraph Vercel
        Build1[Next.js Build]
        CDN[Edge CDN]
    end

    subgraph Railway
        Build2[Docker Build]
        Container[FastAPI Container]
    end

    subgraph Supabase
        PG[(Postgres + pgvector)]
    end

    Repo -->|Push triggers| Build1
    Repo -->|Push triggers| Build2
    Build1 --> CDN
    Build2 --> Container
    Container -->|DATABASE_URL| PG

    User[User Browser] --> CDN
    CDN -->|API calls| Container
```

## Request Lifecycle

```mermaid
flowchart LR
    Browser -->|HTTPS| Vercel
    Vercel -->|Static + SSR| Browser

    Browser -->|API call| Railway
    Railway -->|Auth check: none<br/>CORS check: origin| FastAPI

    FastAPI -->|SQL| Supabase
    FastAPI -->|API| OpenAI

    Supabase -->|Results| FastAPI
    OpenAI -->|Completions| FastAPI
    FastAPI -->|JSON| Browser
```

### Technology Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Frontend framework | Next.js 14 App Router | Server Components by default, fast deploys on Vercel |
| Styling | Tailwind + MD3 tokens | Utility-first, no runtime CSS, consistent design system |
| Backend framework | FastAPI | Async-native, auto docs, Pydantic integration |
| Database | Supabase Postgres | Free tier, managed, pgvector support |
| Vector search | pgvector | Same DB for metadata + vectors, no extra service |
| Embedding model | text-embedding-3-small | Cheap, fast, 1536 dims sufficient for this scale |
| LLM | gpt-4o | Best reasoning for tool selection and grounded Q&A |
| Agent framework | LangChain | Tool orchestration, memory management built-in |
| Deployment | Vercel + Railway | Auto-deploys from GitHub, free tiers |

### Constraints

| Constraint | Value | Reason |
|------------|-------|--------|
| Max documents | 20 | Demo stability, free tier limits |
| Max PDF pages | 20 | Keep ingestion fast and cheap |
| Chunk size | 500 tokens | Balance between context and precision |
| Chunk overlap | 50 tokens | Prevent losing context at boundaries |
| Top K retrieval | 5 | Enough context without overwhelming the LLM |
| Chat memory | 6 messages | Keep context relevant, avoid token bloat |
| Agent max iterations | 5 | Prevent infinite loops |
| LLM temperature | 0.0 | Factual, deterministic answers |
| URL scraping | Static HTML only | BeautifulSoup can't execute JavaScript |
| Auth | None | Single-user portfolio project |

### Security Considerations

*Even though this is a single-user app with no auth:*

| Concern | Mitigation |
|---------|------------|
| API key exposure | Keys in env vars only — never in client code |
| CORS | `ALLOWED_ORIGINS` restricted to Vercel domain |
| SQL injection | Parameterized queries via SQLAlchemy — never string concatenation |
| File upload abuse | 10MB limit, PDF-only content type check |
| Prompt injection | Grounding rules in system prompt; tools are read-only |
| Cost runaway | Max 20 documents; max 5 iterations per agent call |

### Monitoring (Lightweight)

*No dedicated monitoring stack — keep it simple for a portfolio project:*

| What | How |
|------|-----|
| Backend health | `GET /health` — checks DB connection |
| Errors | Railway logs (stdout/stderr) |
| OpenAI spend | OpenAI dashboard usage page |
| DB size | Supabase dashboard → Database → Usage |
| Cold starts | First request after Railway sleep (~10s) — acceptable |