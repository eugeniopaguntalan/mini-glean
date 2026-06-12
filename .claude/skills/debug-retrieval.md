# Skill: Debug Poor RAG Retrieval

## When to Use
- Agent returns "I don't know" for uploaded content
- Wrong document cited
- Answer is vague, off-topic, or hallucinated
- Duplicate or irrelevant chunks returned

---

## Diagnosis Steps

### 1. Confirm the document was ingested
- Check `GET /documents` — doc should appear with `chunk_count > 0`
- If missing → re-ingest
- If `chunk_count` is 0 → parsing failed silently

### 2. Verify chunks exist in the database
```sql
-- Run in Supabase SQL Editor
SELECT id, document_id, chunk_index, LEFT(content, 100)
FROM chunks
WHERE document_id = '<doc-id>'
ORDER BY chunk_index;
```

```text
If no rows → ingestion stored metadata but failed on chunks
If content is garbled → parser issue (pdfplumber or BeautifulSoup)
```

### 3. Test vector search directly

```sql
-- Run a similarity search with a test embedding
SELECT c.id, c.document_id, d.filename,
       LEFT(c.content, 100),
       1 - (c.embedding <=> '<embedding-vector>') AS similarity
FROM chunks c
JOIN documents d ON d.id = c.document_id
ORDER BY c.embedding <=> '<embedding-vector>'
LIMIT 5;
```

```text
If wrong chunks rank highest → query embedding doesn't match content domain
If similarity scores are all low (< 0.3) → content may not be relevant
```

### 4. Inspect chunk quality
- Are chunks cutting mid-sentence? → increase CHUNK_OVERLAP (currently 50)
- Are chunks too broad and unfocused? → decrease CHUNK_SIZE (currently 500)
- Is PDF content garbled? → inspect raw pdfplumber output before embedding

### 5. Verify embedding consistency
- Query and documents must use the same model (text-embedding-3-small)
- Check EMBEDDING_MODEL env var hasn't changed between ingestion runs
- If models were mixed → delete all chunks and re-ingest all documents

### 6. Check the grounding prompt
- Is the system prompt telling the LLM to use only retrieved context?
- If the answer feels like "general knowledge" → the grounding prompt is too weak
- Check prompts/qa.py for the grounding constraint

---

### Common Problems and Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| "I don't know" | Doc not ingested or chunks not relevant | Re-ingest; test search directly via SQL |
| Wrong doc cited | Ambiguous query pulls similar docs | Increase `top_k`; improve query specificity |
| Hallucinated answer | LLM ignoring context | Lower temperature to `0.0`; strengthen grounding prompt |
| Slow retrieval | IVFFlat index not built or stale | Rebuild: `REINDEX INDEX idx_chunks_embedding;` |
| Garbled chunks | Bad PDF parsing | Test `pdfplumber` output; try re-exporting PDF |
| Duplicate chunks | Same doc ingested twice | Delete duplicates; check dedup logic in service |
| Low similarity scores | Wrong embedding model used | Verify `EMBEDDING_MODEL`; re-ingest if changed |

### Key Parameters

| Parameter | Current Value | Location |
|-----------|---------------|----------|
| Chunk size | 500 tokens | `config.py` → `CHUNK_SIZE` |
| Chunk overlap | 50 tokens | `config.py` → `CHUNK_OVERLAP` |
| Top K results | 5 | `config.py` → `TOP_K_RESULTS` |
| Embedding model | text-embedding-3-small | `config.py` → `EMBEDDING_MODEL` |
| Embedding dimensions | 1536 | Hardcoded in schema |
| LLM temperature | 0.0 | `config.py` → `LLM_TEMPERATURE` |
| Vector index type | IVFFlat (lists=10) | docs/database.md |


### Useful SQL Queries

```sql
-- Count chunks per document
SELECT d.filename, d.chunk_count, COUNT(c.id) AS actual_chunks
FROM documents d
LEFT JOIN chunks c ON c.document_id = d.id
GROUP BY d.id;

-- Check embedding dimensions are correct
SELECT id, array_length(embedding::real[], 1) AS dims
FROM chunks
LIMIT 5;
-- Should all return 1536

-- Find orphaned chunks (no parent document)
SELECT c.id FROM chunks c
LEFT JOIN documents d ON d.id = c.document_id
WHERE d.id IS NULL;
```

---

## Rules
- Don't change chunk size/overlap without testing retrieval quality before and after
- Always test with the user's actual query — not a simplified version
- If re-ingesting, delete old chunks first to avoid duplicates
- After bulk re-ingestion, rebuild the IVFFlat index
- All debugging queries go through Supabase SQL Editor or repository — never modify production data without a backup plan
