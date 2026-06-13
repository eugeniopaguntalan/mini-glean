"""
Mock LLM service for demo/portfolio purposes.
Returns pre-canned responses without making real OpenAI API calls.
"""
import asyncio
import random
from typing import AsyncGenerator

# Pre-canned responses for demo questions
MOCK_RESPONSES = {
    "lease": "Based on the rental contract, you need to provide **30 days written notice** to end your lease. The notice must be submitted in writing to the landlord before the end of your rental period.",
    "meeting": "From the team meeting notes, the action items are:\n\n1. **Update API documentation** - Due: Friday, June 20\n2. **Review PR #142** - Due: Tuesday, June 17  \n3. **Schedule client demo** - Due: Next Monday\n\nAll items were assigned during the June 14 standup meeting.",
    "fastapi": "FastAPI is a modern, high-performance Python web framework that uses:\n\n- **Type hints** for automatic validation\n- **Async/await** for concurrent requests\n- **Automatic API docs** via OpenAPI\n- **Pydantic** for data validation\n\nIt's particularly well-suited for building REST APIs and microservices.",
    "compare": "**Similarities:**\nBoth documents discuss technical implementation details and best practices.\n\n**Differences:**\n- The rental contract is a legal document with specific clauses and obligations\n- The FastAPI notes are educational content focused on web development\n- Different purposes: legal agreement vs. learning material",
    "default": "I found relevant information in your knowledge base. The documents contain details that may help answer your question, though I recommend reviewing the source documents directly for complete context.",
}

# Mock embeddings (random vectors for demo)
def mock_embedding(text: str) -> list[float]:
    """Generate a deterministic pseudo-random embedding for demo purposes."""
    random.seed(hash(text) % (2**32))  # Deterministic based on input
    return [random.random() for _ in range(1536)]


async def mock_stream_response(text: str) -> AsyncGenerator[str, None]:
    """Stream response token by token to simulate real LLM streaming."""
    words = text.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.05)  # Simulate network delay


def get_mock_response(question: str) -> str:
    """Select appropriate mock response based on question keywords."""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ["lease", "rental", "notice", "contract"]):
        return MOCK_RESPONSES["lease"]
    elif any(word in question_lower for word in ["meeting", "action", "items", "due"]):
        return MOCK_RESPONSES["meeting"]
    elif any(word in question_lower for word in ["fastapi", "python", "framework", "api"]):
        return MOCK_RESPONSES["fastapi"]
    elif "compare" in question_lower:
        return MOCK_RESPONSES["compare"]
    else:
        return MOCK_RESPONSES["default"]


# Mock source documents (matches the seeded demo data)
MOCK_SOURCES = {
    "lease": ["doc-001"],  # rental-contract.pdf
    "meeting": ["doc-003"],  # meeting-notes.txt
    "fastapi": ["doc-002"],  # fastapi-notes.pdf
    "compare": ["doc-001", "doc-002"],
    "default": ["doc-001", "doc-002", "doc-003"],
}


def get_mock_sources(question: str) -> list[str]:
    """Return mock source document IDs based on question."""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ["lease", "rental", "notice", "contract"]):
        return MOCK_SOURCES["lease"]
    elif any(word in question_lower for word in ["meeting", "action", "items", "due"]):
        return MOCK_SOURCES["meeting"]
    elif any(word in question_lower for word in ["fastapi", "python", "framework", "api"]):
        return MOCK_SOURCES["fastapi"]
    elif "compare" in question_lower:
        return MOCK_SOURCES["compare"]
    else:
        return MOCK_SOURCES["default"]
