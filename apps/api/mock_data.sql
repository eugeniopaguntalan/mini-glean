-- Mock data for portfolio demo
-- Pre-populated documents with embeddings for offline demo

-- Insert documents
INSERT INTO documents (id, filename, type, tags, chunk_count, created_at) VALUES
('doc-001', 'rental-contract.pdf', 'pdf', ARRAY['legal', 'rental'], 8, NOW()),
('doc-002', 'fastapi-notes.pdf', 'pdf', ARRAY['tech', 'python'], 6, NOW()),
('doc-003', 'Team Meeting - June 14', 'note', ARRAY['meeting', 'action-items'], 4, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert chunks with mock embeddings
-- Note: These are random vectors for demo purposes
-- In a real system, these would be actual embeddings from the content

-- rental-contract.pdf chunks
INSERT INTO chunks (id, document_id, content, chunk_index, embedding) VALUES
('chunk-001-1', 'doc-001', 
'RESIDENTIAL LEASE AGREEMENT

This Lease Agreement ("Agreement") is entered into on January 1, 2026, between John Smith ("Landlord") and Jane Doe ("Tenant").

TERM: This lease shall be for a period of one year, commencing on February 1, 2026 and ending on January 31, 2027.',
0, (SELECT array_agg(random()) FROM generate_series(1, 1536))),

('chunk-001-2', 'doc-001',
'RENT: Tenant agrees to pay monthly rent of $2,000, due on the first day of each month. Late payments will incur a $50 fee after the 5th day of the month.',
1, (SELECT array_agg(random()) FROM generate_series(1, 1536))),

('chunk-001-3', 'doc-001',
'TERMINATION: Either party may terminate this lease by providing 30 days written notice to the other party before the end of the rental period. Notice must be submitted in writing via certified mail or email.',
2, (SELECT array_agg(random()) FROM generate_series(1, 1536))),

('chunk-001-4', 'doc-001',
'SECURITY DEPOSIT: Tenant has paid a security deposit of $2,000. This deposit will be returned within 30 days of lease termination, less any deductions for damages beyond normal wear and tear.',
3, (SELECT array_agg(random()) FROM generate_series(1, 1536)))
ON CONFLICT (id) DO NOTHING;

-- fastapi-notes.pdf chunks  
INSERT INTO chunks (id, document_id, content, chunk_index, embedding) VALUES
('chunk-002-1', 'doc-002',
'FastAPI Study Notes - Chapter 1

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

Key Features:
- Fast: Very high performance, on par with NodeJS and Go
- Fast to code: Increase development speed by 200-300%
- Fewer bugs: Reduce human errors by about 40%',
0, (SELECT array_agg(random()) FROM generate_series(1, 1536))),

('chunk-002-2', 'doc-002',
'Type Hints and Validation

FastAPI uses Pydantic for data validation:
- Automatic request validation based on type hints
- Clear error messages when validation fails
- Editor support with autocomplete
- Reduces need for manual validation code',
1, (SELECT array_agg(random()) FROM generate_series(1, 1536))),

('chunk-002-3', 'doc-002',
'Async Support

FastAPI has excellent async/await support:
- Use async def for async endpoints
- Concurrent request handling
- Better performance for I/O-bound operations
- Compatible with SQLAlchemy, asyncpg, httpx, etc.',
2, (SELECT array_agg(random()) FROM generate_series(1, 1536))),

('chunk-002-4', 'doc-002',
'Automatic API Documentation

FastAPI automatically generates:
- Interactive API docs (Swagger UI) at /docs
- Alternative API docs (ReDoc) at /redoc
- OpenAPI schema at /openapi.json
- All derived from your code and type hints',
3, (SELECT array_agg(random()) FROM generate_series(1, 1536)))
ON CONFLICT (id) DO NOTHING;

-- meeting-notes chunks
INSERT INTO chunks (id, document_id, content, chunk_index, embedding) VALUES
('chunk-003-1', 'doc-003',
'Team Standup Meeting - June 14, 2026

Attendees: Sarah (PM), Mike (Dev), Lisa (Design), James (QA)

Sprint Progress:
- API endpoints: 80% complete
- Frontend components: 60% complete
- Testing: 40% complete',
0, (SELECT array_agg(random()) FROM generate_series(1, 1536))),

('chunk-003-2', 'doc-003',
'Action Items:

1. Update API documentation
   - Assignee: Mike
   - Due: Friday, June 20
   - Status: Not started

2. Review PR #142 (auth improvements)
   - Assignee: Sarah
   - Due: Tuesday, June 17
   - Status: In progress',
1, (SELECT array_agg(random()) FROM generate_series(1, 1536))),

('chunk-003-3', 'doc-003',
'3. Schedule client demo
   - Assignee: Sarah
   - Due: Next Monday (June 22)
   - Status: Not started

4. Fix responsive layout issues
   - Assignee: Lisa
   - Due: Wednesday, June 18
   - Status: In progress',
2, (SELECT array_agg(random()) FROM generate_series(1, 1536))),

('chunk-003-4', 'doc-003',
'Blockers:
- Waiting on backend deployment (Mike working on it)
- Design system update delayed until next sprint

Next Meeting: Monday, June 22 at 10am',
3, (SELECT array_agg(random()) FROM generate_series(1, 1536)))
ON CONFLICT (id) DO NOTHING;
