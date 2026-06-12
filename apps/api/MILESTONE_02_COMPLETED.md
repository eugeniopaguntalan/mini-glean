# Milestone 2 Implementation - Document Ingestion

## ✅ Completed Implementation

### 1. Dependencies Added
- pdfplumber==0.10.4
- beautifulsoup4==4.12.3
- tiktoken==0.5.2
- openai==1.12.0
- reportlab==4.0.9 (for test fixtures)

### 2. Schemas Defined (`schemas.py`)
- DocumentResponse
- DocumentListResponse
- UrlIngestRequest
- NoteIngestRequest
- ErrorResponse

### 3. Custom Exceptions (`services/exceptions.py`)
- DocumentNotFoundError
- DocumentLimitExceededError
- InvalidFileTypeError
- FileTooLargeError
- PageLimitExceededError
- ParseError
- EmbeddingError

### 4. Services Implemented

#### Parser Service (`services/parser.py`)
- `parse_pdf(content: bytes) → str` - Extracts text from PDF, validates page count
- `parse_url(url: str) → tuple[str, str]` - Fetches and parses HTML, returns (text, title)
- `parse_note(content: str) → str` - Validates and returns note content

#### Chunker Service (`services/chunker.py`)
- `chunk_text(text, chunk_size=500, overlap=50) → list[str]` - Splits text into token-sized chunks
- Uses tiktoken with cl100k_base encoding
- Preserves sentence boundaries
- Merges tiny last chunks (<50 tokens)

#### Embedder Service (`services/embedder.py`)
- `embed_chunks(chunks) → list[list[float]]` - Batch embeds chunks (batches of 20)
- `embed_query(query) → list[float]` - Embeds single query
- Uses OpenAI text-embedding-3-small (1536 dimensions)

#### Document Service (`services/document_service.py`)
- `ingest_pdf(file_content, filename, session)` - Full PDF ingestion pipeline
- `ingest_url(url, session)` - Full URL ingestion pipeline
- `ingest_note(content, tags, session)` - Full note ingestion pipeline
- `list_documents(session)` - Lists all documents
- `delete_document(doc_id, session)` - Deletes document with cascade

All services check document limit FIRST (fail fast) before processing.

### 5. Router Implemented (`routers/documents.py`)
- POST /documents/upload/pdf - Upload PDF (validates type & size)
- POST /documents/url - Ingest URL
- POST /documents/note - Create note
- GET /documents - List all documents
- DELETE /documents/{doc_id} - Delete document

All exceptions properly mapped to HTTP status codes:
- 400: Document limit exceeded
- 404: Document not found
- 413: File too large
- 415: Invalid file type
- 422: Parse error or page limit exceeded
- 502: Embedding service error

### 6. Router Registered in `main.py`
✅ Documents router included in FastAPI app

### 7. Unit Tests Written
- `tests/unit/test_chunker.py` - 8 tests covering chunking logic
- `tests/unit/test_parser.py` - 9 tests covering PDF/URL/note parsing
- `tests/unit/test_embedder.py` - 6 tests covering embedding generation
- `tests/unit/test_document_service.py` - 9 tests covering full ingestion pipeline

All tests use proper mocking - no real OpenAI calls or database operations.

### 8. Test Infrastructure
- Created test directory structure
- Script to generate sample PDF: `create_test_pdf.py`

## 🔧 Verification Steps Required

### Prerequisites
```bash
# 1. Rebuild API container with new dependencies
docker-compose build api

# 2. Restart services
docker-compose up -d

# 3. Create test PDF fixture
docker-compose exec api python create_test_pdf.py
```

### Run Unit Tests
```bash
# Run all unit tests
docker-compose exec api pytest tests/unit/ -v

# Should see all tests passing:
# - test_chunker.py: 8 passed
# - test_parser.py: 9 passed  
# - test_embedder.py: 6 passed
# - test_document_service.py: 9 passed
# Total: 32 tests passed
```

### Lint Check
```bash
docker-compose exec api ruff check .
# Should show: All checks passed!
```

### Integration Tests (Manual)

#### 1. Upload PDF
```bash
curl -X POST http://localhost:8000/documents/upload/pdf \
  -F "file=@apps/api/tests/fixtures/sample.pdf"
# Expected: 201 Created with DocumentResponse
```

#### 2. Ingest URL
```bash
curl -X POST http://localhost:8000/documents/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
# Expected: 201 Created
```

#### 3. Create Note
```bash
curl -X POST http://localhost:8000/documents/note \
  -H "Content-Type: application/json" \
  -d '{"content": "This is a test note about Python programming.", "tags": ["python", "test"]}'
# Expected: 201 Created
```

#### 4. List Documents
```bash
curl http://localhost:8000/documents
# Expected: Array of 3 documents
```

#### 5. Verify Database
```bash
# Check chunk counts match
docker-compose exec db psql -U postgres -d miniglean \
  -c "SELECT d.filename, d.chunk_count, COUNT(c.id) as actual_chunks FROM documents d LEFT JOIN chunks c ON c.document_id = d.id GROUP BY d.id;"

# Verify embedding dimensions
docker-compose exec db psql -U postgres -d miniglean \
  -c "SELECT id, vector_dims(embedding) FROM chunks LIMIT 3;"
# All should return 1536
```

#### 6. Test Delete with Cascade
```bash
# Get a document ID from list, then:
curl -X DELETE http://localhost:8000/documents/<doc-id>
# Expected: 204 No Content

# Verify chunks were deleted (cascade)
docker-compose exec db psql -U postgres -d miniglean \
  -c "SELECT COUNT(*) FROM chunks WHERE document_id = '<doc-id>';"
# Expected: 0
```

#### 7. Test Document Limit
Upload 20 documents, then attempt a 21st:
```bash
# Should return 400: "Maximum document limit (20) reached"
```

#### 8. Test Invalid PDF
```bash
curl -X POST http://localhost:8000/documents/upload/pdf \
  -F "file=@README.md"
# Expected: 415 Unsupported Media Type
```

#### 9. Test File Size Limit
Upload a PDF > 10MB:
```bash
# Expected: 413 Request Entity Too Large
```

## 📝 Implementation Notes

### Design Decisions Followed
✅ Fail fast: Document limit checked before parsing/embedding
✅ Batch embedding: Chunks processed in groups of 20
✅ Sentence boundaries preserved in chunking
✅ File validation in router (content type & size)
✅ Proper exception hierarchy and HTTP status mapping
✅ Repository pattern for DB access
✅ Service layer for business logic
✅ No business logic in routers

### Code Quality
✅ All functions fully implemented (no placeholders)
✅ Type hints on all function signatures
✅ Docstrings on public service methods
✅ Proper async/await usage
✅ Error handling with custom exceptions
✅ Mocked external services in tests

### Parameters Configured
- CHUNK_SIZE: 500 (from config.py)
- CHUNK_OVERLAP: 50 (from config.py)
- MAX_DOCUMENTS: 20 (from config.py)
- EMBEDDING_MODEL: text-embedding-3-small (from config.py)
- MAX_FILE_SIZE: 10MB (in router)
- MAX_PDF_PAGES: 20 (in parser)
- EMBEDDING_BATCH_SIZE: 20 (in embedder)
- URL_FETCH_TIMEOUT: 10 seconds (in parser)

## ⚠️ Known Issues
- Terminal display issues prevented running verification steps during implementation
- Test PDF needs to be generated using `create_test_pdf.py` script
- Requires OPENAI_API_KEY environment variable to be set for actual API calls

## ✅ Ready for Testing
All code is implemented and ready for verification. Run the steps above to confirm:
1. All unit tests pass
2. ruff check passes
3. All API endpoints work correctly
4. Database CASCADE deletes work
5. Document limit is enforced
6. File validation works
