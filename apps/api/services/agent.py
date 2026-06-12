"""
Agent Service
Builds and invokes the LangChain agent with tools and per-session memory
"""

import re
from dataclasses import dataclass, field
from typing import AsyncGenerator, List, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from prompts.system import AGENT_SYSTEM_PROMPT
from services import llm
from services.memory import session_store
from tools.search_knowledge_base import make_search_tool
from tools.summarize_document import make_summarize_tool
from tools.compare_documents import make_compare_tool
from tools.add_note import make_add_note_tool


# Maximum agent reasoning loops before stopping
MAX_ITERATIONS = 5

# Matches [source: doc_id] and [sources: id_a, id_b]
_SOURCE_PATTERN = re.compile(
    r"\[sources?:\s*([a-f0-9][a-f0-9\-,\s]*)\]",
    re.IGNORECASE,
)


@dataclass
class AgentResponse:
    """Structured result of an agent invocation"""
    content: str
    tool_used: Optional[str] = None
    source_doc_ids: List[str] = field(default_factory=list)


def build_tools(session: AsyncSession) -> List[BaseTool]:
    """
    Build the 4 agent tools bound to a database session

    Args:
        session: The active database session for this request

    Returns:
        List of 4 StructuredTool instances
    """
    return [
        make_search_tool(session),
        make_summarize_tool(session),
        make_compare_tool(session),
        make_add_note_tool(session),
    ]


def build_agent(
    tools: List[BaseTool],
    system_prompt: str = AGENT_SYSTEM_PROMPT,
) -> AgentExecutor:
    """
    Build a LangChain agent executor with the given tools

    Args:
        tools: The tools to register with the agent
        system_prompt: The system prompt governing agent behaviour

    Returns:
        A configured AgentExecutor
    """
    model = llm.get_chat_model()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(model, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        max_iterations=MAX_ITERATIONS,
        handle_parsing_errors=True,
        verbose=settings.ENVIRONMENT == "development",
        return_intermediate_steps=True,
    )


def _parse_source_ids(content: str) -> List[str]:
    """
    Extract source document IDs from agent response content

    Handles both [source: id] and [sources: id_a, id_b] formats.

    Args:
        content: The agent response text

    Returns:
        Deduplicated list of document IDs in order of first appearance
    """
    doc_ids: List[str] = []
    for match in _SOURCE_PATTERN.finditer(content):
        raw = match.group(1)
        for part in raw.split(","):
            doc_id = part.strip()
            if doc_id and doc_id not in doc_ids:
                doc_ids.append(doc_id)
    return doc_ids


async def invoke(
    question: str,
    session_id: str,
    session: AsyncSession,
) -> AgentResponse:
    """
    Invoke the agent for a question within a conversation session

    Args:
        question: The user's question
        session_id: The conversation session identifier
        session: The active database session for tool execution

    Returns:
        AgentResponse with content, tool used, and cited source doc IDs
    """
    # Load prior conversation history (last 6 exchanges)
    history = session_store.get_history(session_id)

    # Build session-bound tools and the agent executor
    tools = build_tools(session)
    executor = build_agent(tools)

    # Run the agent
    result = await executor.ainvoke({
        "input": question,
        "chat_history": history,
    })

    content = result.get("output", "")

    # Determine which tool was used from the intermediate steps
    tool_used: Optional[str] = None
    steps = result.get("intermediate_steps", [])
    if steps:
        last_action = steps[-1][0]
        tool_used = getattr(last_action, "tool", None)

    # Extract cited source document IDs
    source_doc_ids = _parse_source_ids(content)

    # Persist the exchange to session memory
    session_store.add_exchange(session_id, question, content)

    return AgentResponse(
        content=content,
        tool_used=tool_used,
        source_doc_ids=source_doc_ids,
    )


async def astream(
    question: str,
    session_id: str,
    session: AsyncSession,
) -> AsyncGenerator[str, None]:
    """
    Stream the agent's final answer token by token

    Uses LangChain's event stream and yields only the tokens that make up the
    final answer (chat-model stream chunks with non-empty content). Tool-call
    planning chunks carry empty content and are therefore skipped. The full
    answer is persisted to session memory once streaming completes.

    Args:
        question: The user's question
        session_id: The conversation session identifier
        session: The active database session for tool execution

    Yields:
        Answer tokens in order as they are generated
    """
    history = session_store.get_history(session_id)
    tools = build_tools(session)
    executor = build_agent(tools)

    collected: List[str] = []
    async for event in executor.astream_events(
        {"input": question, "chat_history": history},
        version="v1",
    ):
        if event["event"] != "on_chat_model_stream":
            continue
        chunk = event["data"].get("chunk")
        token = getattr(chunk, "content", "") if chunk is not None else ""
        if token:
            collected.append(token)
            yield token

    # Persist the completed exchange to session memory
    content = "".join(collected)
    session_store.add_exchange(session_id, question, content)
