"""
Summarize Document Tool
Generates a concise summary of a single document by its ID
"""

from langchain_core.tools import StructuredTool, ToolException
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.chunk_repository import ChunkRepository
from services import llm
from tools.schemas import SummarizeInput


SUMMARIZE_DESCRIPTION = (
    "Summarizes a specific document by its ID.\n"
    "Use this when the user says 'summarize', 'give me a summary', "
    "or 'what's in document X'.\n"
    "Retrieves all chunks from that document and generates a concise summary."
)


async def summarize_document(
    doc_id: str,
    chunk_repo: ChunkRepository,
) -> str:
    """
    Summarize a document by concatenating its chunks and calling the LLM

    Args:
        doc_id: The document ID to summarize
        chunk_repo: Repository for chunk database access

    Returns:
        A summary string with a source citation, or a "not found" message

    Raises:
        ToolException: If the summarization fails due to a system error
    """
    try:
        chunks = await chunk_repo.get_by_document_id(doc_id)

        if not chunks:
            return f"No document found with ID '{doc_id}'"

        content = "\n\n".join(chunk.content for chunk in chunks)
        summary = llm.summarize(content)

        return f"[source: {doc_id}]\n{summary}"

    except ToolException:
        raise
    except Exception as e:
        raise ToolException(f"Summarize failed: {str(e)}")


def make_summarize_tool(session: AsyncSession) -> StructuredTool:
    """
    Build a summarize_document StructuredTool bound to a database session

    Args:
        session: The active database session for this request

    Returns:
        A LangChain StructuredTool ready for agent registration
    """
    chunk_repo = ChunkRepository(session)

    async def _run(doc_id: str) -> str:
        return await summarize_document(doc_id, chunk_repo)

    return StructuredTool.from_function(
        coroutine=_run,
        name="summarize_document",
        description=SUMMARIZE_DESCRIPTION,
        args_schema=SummarizeInput,
        handle_tool_error=True,
    )
