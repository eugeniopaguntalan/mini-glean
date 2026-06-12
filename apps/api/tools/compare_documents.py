"""
Compare Documents Tool
Compares two documents and highlights similarities and differences
"""

from langchain_core.tools import StructuredTool, ToolException
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.chunk_repository import ChunkRepository
from services import llm
from tools.schemas import CompareInput


COMPARE_DESCRIPTION = (
    "Compares two documents and highlights their key differences and similarities.\n"
    "Use this when the user says 'compare X and Y' or "
    "'what's different between A and B'.\n"
    "Requires two document IDs — ask the user to clarify if only one is provided."
)


async def compare_documents(
    doc_id_a: str,
    doc_id_b: str,
    chunk_repo: ChunkRepository,
) -> str:
    """
    Compare two documents by concatenating chunks and calling the LLM

    Args:
        doc_id_a: The first document ID
        doc_id_b: The second document ID
        chunk_repo: Repository for chunk database access

    Returns:
        A comparison string with both source citations, or a "not found" message

    Raises:
        ToolException: If the comparison fails due to a system error
    """
    try:
        chunks_a = await chunk_repo.get_by_document_id(doc_id_a)
        if not chunks_a:
            return f"Document '{doc_id_a}' not found"

        chunks_b = await chunk_repo.get_by_document_id(doc_id_b)
        if not chunks_b:
            return f"Document '{doc_id_b}' not found"

        content_a = "\n\n".join(chunk.content for chunk in chunks_a)
        content_b = "\n\n".join(chunk.content for chunk in chunks_b)

        comparison = llm.compare(content_a, content_b, doc_id_a, doc_id_b)

        return f"[sources: {doc_id_a}, {doc_id_b}]\n{comparison}"

    except ToolException:
        raise
    except Exception as e:
        raise ToolException(f"Compare failed: {str(e)}")


def make_compare_tool(session: AsyncSession) -> StructuredTool:
    """
    Build a compare_documents StructuredTool bound to a database session

    Args:
        session: The active database session for this request

    Returns:
        A LangChain StructuredTool ready for agent registration
    """
    chunk_repo = ChunkRepository(session)

    async def _run(doc_id_a: str, doc_id_b: str) -> str:
        return await compare_documents(doc_id_a, doc_id_b, chunk_repo)

    return StructuredTool.from_function(
        coroutine=_run,
        name="compare_documents",
        description=COMPARE_DESCRIPTION,
        args_schema=CompareInput,
        handle_tool_error=True,
    )
