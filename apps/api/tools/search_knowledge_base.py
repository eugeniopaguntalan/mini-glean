"""
Search Knowledge Base Tool
Semantic similarity search over the user's uploaded documents
"""

from langchain_core.tools import StructuredTool, ToolException
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.chunk_repository import ChunkRepository
from services import embedder
from tools.schemas import SearchInput


SEARCH_DESCRIPTION = (
    "Search the user's personal knowledge base using semantic similarity.\n"
    "Use this when the user asks a question about something they may have uploaded.\n"
    "Returns relevant text chunks with their source document IDs.\n"
    "Do NOT use this for summarizing or comparing — use the dedicated tools for those."
)

# Chunks below this cosine similarity are considered irrelevant
SIMILARITY_THRESHOLD = 0.3


async def search_knowledge_base(
    query: str,
    top_k: int,
    chunk_repo: ChunkRepository,
) -> str:
    """
    Search the knowledge base and return formatted relevant chunks

    Args:
        query: The search query
        top_k: Maximum number of chunks to retrieve
        chunk_repo: Repository for chunk database access

    Returns:
        Formatted string of relevant chunks, or a "not found" message

    Raises:
        ToolException: If the search fails due to a system error
    """
    try:
        embedding = embedder.embed_query(query)
        results = await chunk_repo.search_similar(embedding, top_k)

        formatted = []
        for result in results:
            similarity = 1.0 - result["distance"]
            if similarity > SIMILARITY_THRESHOLD:
                formatted.append(
                    f"[source: {result['document_id']} | {result['filename']}]\n"
                    f"{result['content']}"
                )

        if not formatted:
            return "No relevant documents found"

        return "\n\n---\n\n".join(formatted)

    except Exception as e:
        raise ToolException(f"Search failed: {str(e)}")


def make_search_tool(session: AsyncSession) -> StructuredTool:
    """
    Build a search_knowledge_base StructuredTool bound to a database session

    Args:
        session: The active database session for this request

    Returns:
        A LangChain StructuredTool ready for agent registration
    """
    chunk_repo = ChunkRepository(session)

    async def _run(query: str, top_k: int = 5) -> str:
        return await search_knowledge_base(query, top_k, chunk_repo)

    return StructuredTool.from_function(
        coroutine=_run,
        name="search_knowledge_base",
        description=SEARCH_DESCRIPTION,
        args_schema=SearchInput,
        handle_tool_error=True,
    )
