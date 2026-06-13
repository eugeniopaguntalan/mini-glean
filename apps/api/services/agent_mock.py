"""
Mock Agent Service
Returns pre-canned responses for demo without calling OpenAI
"""

import asyncio
from typing import AsyncGenerator, Optional
from dataclasses import dataclass, field

from config import settings


@dataclass
class AgentResponse:
    """Structured result of an agent invocation"""
    content: str
    tool_used: Optional[str] = None
    source_doc_ids: list[str] = field(default_factory=list)


# Pre-canned responses mapped by keywords
MOCK_RESPONSES = {
    "lease|rental|notice|contract|end": {
        "content": "Based on the rental contract, you need to provide **30 days written notice** to end your lease. The notice must be submitted in writing to the landlord before the end of your rental period. [source: doc-001]",
        "tool": "search_knowledge_base",
        "sources": ["doc-001"],
    },
    "meeting|action|items|due|team": {
        "content": "From the team meeting notes, the action items are:\n\n1. **Update API documentation** - Due: Friday, June 20\n2. **Review PR #142** - Due: Tuesday, June 17\n3. **Schedule client demo** - Due: Next Monday\n\nAll items were assigned during the June 14 standup meeting. [source: doc-003]",
        "tool": "search_knowledge_base",
        "sources": ["doc-003"],
    },
    "fastapi|python|framework|api": {
        "content": "FastAPI is a modern, high-performance Python web framework that uses:\n\n- **Type hints** for automatic validation\n- **Async/await** for concurrent requests\n- **Automatic API docs** via OpenAPI\n- **Pydantic** for data validation\n\nIt's particularly well-suited for building REST APIs and microservices. [source: doc-002]",
        "tool": "search_knowledge_base",
        "sources": ["doc-002"],
    },
    "compare": {
        "content": "**Similarities:**\nBoth documents contain structured information with specific requirements and guidelines.\n\n**Differences:**\n- The rental contract is a legal document with binding obligations\n- The FastAPI notes are educational content focused on technical implementation\n- Different purposes: legal agreement vs. learning material\n\n[sources: doc-001, doc-002]",
        "tool": "compare_documents",
        "sources": ["doc-001", "doc-002"],
    },
    "summarize": {
        "content": "This document provides comprehensive information on the topic with clear explanations and specific examples. Key points are well-organized and easy to follow. [source: doc-001]",
        "tool": "summarize_document",
        "sources": ["doc-001"],
    },
}


DEFAULT_RESPONSE = {
    "content": "I found relevant information in your knowledge base. The documents contain details that may help answer your question. For more specific information, try asking about:\n- Rental contract and lease terms\n- Team meeting action items\n- FastAPI framework features\n\n[sources: doc-001, doc-002, doc-003]",
    "tool": "search_knowledge_base",
    "sources": ["doc-001", "doc-002", "doc-003"],
}


def _match_response(question: str) -> dict:
    """Match question to appropriate mock response."""
    question_lower = question.lower()
    
    import re
    for pattern, response in MOCK_RESPONSES.items():
        if re.search(pattern, question_lower):
            return response
    
    return DEFAULT_RESPONSE


async def invoke(
    question: str,
    session_id: str,
    session,  # Not used in mock mode but matches real signature
) -> AgentResponse:
    """
    Mock agent invocation - returns pre-canned response.
    
    Args:
        question: The user's question
        session_id: The conversation session identifier
        session: Database session (unused in mock mode)
        
    Returns:
        AgentResponse with mock content and sources
    """
    # Simulate thinking delay
    await asyncio.sleep(0.3)
    
    response_data = _match_response(question)
    
    return AgentResponse(
        content=response_data["content"],
        tool_used=response_data["tool"],
        source_doc_ids=response_data["sources"],
    )


async def stream(
    question: str,
    session_id: str,
    session,
) -> AsyncGenerator[str, None]:
    """
    Mock streaming response - yields tokens one at a time.
    
    Args:
        question: The user's question
        session_id: Session identifier
        session: Database session (unused)
        
    Yields:
        Individual tokens of the response
    """
    response_data = _match_response(question)
    words = response_data["content"].split()
    
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.05)  # Simulate streaming delay
