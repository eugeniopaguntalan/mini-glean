"""
Tool Input Schemas
Pydantic models defining the inputs for each agent tool.
The agent reads the Field descriptions to understand expected inputs.
"""

from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field


class SearchInput(BaseModel):
    """Input schema for the search_knowledge_base tool"""
    query: str = Field(
        description="The search query describing what the user is looking for."
    )
    top_k: int = Field(
        default=5,
        description="The maximum number of relevant chunks to retrieve."
    )


class SummarizeInput(BaseModel):
    """Input schema for the summarize_document tool"""
    doc_id: str = Field(
        description="The unique ID of the document to summarize."
    )


class CompareInput(BaseModel):
    """Input schema for the compare_documents tool"""
    doc_id_a: str = Field(
        description="The unique ID of the first document to compare."
    )
    doc_id_b: str = Field(
        description="The unique ID of the second document to compare."
    )


class AddNoteInput(BaseModel):
    """Input schema for the add_note tool"""
    content: str = Field(
        description="The plain text content of the note to save."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Optional list of tags to categorize the note."
    )
