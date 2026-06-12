# Skill: Add a RAG Agent Tool

## When to Use
- Adding a new capability the LangChain agent can invoke
- Modifying what an existing tool returns
- Debugging why the agent picks the wrong tool

---

## How It Works

User question → Agent reads tool docstrings → Picks tool → Calls it → LLM generates answer

The **docstring IS the tool description**. The agent reads it to decide which tool to call.

---

## Steps

1. Add input schema to `apps/api/tools/schemas.py` — use `Field(description=...)`
2. Create tool file in `apps/api/tools/<tool_name>.py`
3. Write a clear, specific docstring — state when TO use and when NOT TO use
4. Use `repositories/chunk_repository.py` for vector search — never query DB directly
5. Use `services/llm.py` for any LLM calls — never instantiate OpenAI directly
6. Handle the "not found" case with a helpful string return
7. Raise `ToolException` only for system errors
8. Include `[source: doc_id]` in output for citation rendering
9. Register in `TOOLS` list in `apps/api/services/agent.py`
10. Write tests covering: happy path, not found, system error

---

## Conventions

**Location**: `apps/api/tools/` — one file per tool
**Input**: Always use Pydantic schema with `Field(description=...)`
**Output**: Plain formatted string — the LLM reads this
**DB access**: Through repository — injected or imported from `repositories/`
**LLM calls**: Through `services/llm.py` — never instantiate directly
**Citations**: Always include `[source: doc_id]` in output

**Dependency Flow**

```text
Tool → Repository → pgvector (similarity search)
→ LLM Service → OpenAI (summarize, compare)
```

---

## Docstring Rules
- First line: what it does
- Second line: when the agent should use it
- Third line: what it returns
- Optional: when NOT to use it (to prevent wrong tool selection)

---

## Rules
- Tools are read-only — no DB writes (except `add_note` explicitly)
- "Not found" → return helpful string, don't raise
- System error → raise `ToolException`
- One tool = one responsibility — if it does two things, split it
- Keep output human-readable — the LLM reads it, not a machine
- Never write raw SQL in tools — go through chunk_repository

---

## Current Tools Registry

| Tool | When Agent Uses It |
|---|---|
| `search_knowledge_base` | User asks a question about uploaded content |
| `summarize_document` | User asks to summarize a specific doc |
| `compare_documents` | User asks to compare two docs |
| `add_note` | User wants to save something |

---

## Checklist
- [ ] Input schema in `tools/schemas.py` with `Field(description=...)`
- [ ] Tool file in `apps/api/tools/`
- [ ] Docstring states when TO use and when NOT TO use
- [ ] DB access goes through repository — not raw SQL in the tool
- [ ] LLM calls go through `services/llm.py`
- [ ] "Not found" returns helpful string
- [ ] System errors raise `ToolException`
- [ ] Output includes `[source: doc_id]`
- [ ] Registered in `TOOLS` list in `services/agent.py`
- [ ] Tests cover happy path, not found, system error