"""
Add Note Tool
Saves a plain text note to the knowledge base. The only tool that writes data.
"""

from typing import List
from langchain_core.tools import StructuredTool, ToolException
from sqlalchemy.ext.asyncio import AsyncSession
from services import document_service
from tools.schemas import AddNoteInput


ADD_NOTE_DESCRIPTION = (
    "Saves a plain text note to the knowledge base.\n"
    "Use this when the user says 'save this', 'remember this', or 'add a note'.\n"
    "The note is chunked, embedded, and made searchable immediately."
)


async def add_note(
    content: str,
    tags: List[str],
    session: AsyncSession,
) -> str:
    """
    Save a note to the knowledge base

    Args:
        content: The note content
        tags: Optional tags for the note
        session: Database session

    Returns:
        A confirmation message including the new document ID and chunk count

    Raises:
        ToolException: If saving the note fails due to a system error
    """
    try:
        document = await document_service.ingest_note(content, tags, session)
        return (
            f"Note saved with ID '{document.id}' "
            f"and {document.chunk_count} chunk(s)."
        )
    except Exception as e:
        raise ToolException(f"Add note failed: {str(e)}")


def make_add_note_tool(session: AsyncSession) -> StructuredTool:
    """
    Build an add_note StructuredTool bound to a database session

    Args:
        session: The active database session for this request

    Returns:
        A LangChain StructuredTool ready for agent registration
    """

    async def _run(content: str, tags: List[str] = []) -> str:
        return await add_note(content, tags, session)

    return StructuredTool.from_function(
        coroutine=_run,
        name="add_note",
        description=ADD_NOTE_DESCRIPTION,
        args_schema=AddNoteInput,
        handle_tool_error=True,
    )
