"""
Unit Tests for the Agent Service
"""

from unittest.mock import MagicMock, patch

from langchain.agents import AgentExecutor

from services.agent import build_tools, build_agent, MAX_ITERATIONS, _parse_source_ids


def _fake_chat_model():
    """A stand-in ChatOpenAI that satisfies create_openai_tools_agent"""
    model = MagicMock()
    # create_openai_tools_agent calls bind_tools on the model
    model.bind_tools.return_value = MagicMock()
    return model


def test_build_tools_returns_four_tools():
    """The agent is wired with exactly the 4 expected tools"""
    session = MagicMock()
    tools = build_tools(session)

    assert len(tools) == 4
    names = {tool.name for tool in tools}
    assert names == {
        "search_knowledge_base",
        "summarize_document",
        "compare_documents",
        "add_note",
    }


def test_build_agent_returns_executor():
    """build_agent returns an AgentExecutor without error"""
    session = MagicMock()
    tools = build_tools(session)

    with patch("services.agent.llm.get_chat_model", return_value=_fake_chat_model()):
        executor = build_agent(tools)

    assert isinstance(executor, AgentExecutor)


def test_agent_has_four_tools_registered():
    """The executor exposes all 4 tools"""
    session = MagicMock()
    tools = build_tools(session)

    with patch("services.agent.llm.get_chat_model", return_value=_fake_chat_model()):
        executor = build_agent(tools)

    assert len(executor.tools) == 4


def test_max_iterations_is_five():
    """The executor stops after at most 5 iterations"""
    session = MagicMock()
    tools = build_tools(session)

    with patch("services.agent.llm.get_chat_model", return_value=_fake_chat_model()):
        executor = build_agent(tools)

    assert MAX_ITERATIONS == 5
    assert executor.max_iterations == 5


def test_handle_parsing_errors_enabled():
    """Malformed tool calls are handled gracefully"""
    session = MagicMock()
    tools = build_tools(session)

    with patch("services.agent.llm.get_chat_model", return_value=_fake_chat_model()):
        executor = build_agent(tools)

    assert executor.handle_parsing_errors is True


def test_parse_source_ids_dedupes_and_orders():
    """Source IDs are extracted, deduplicated, and ordered by appearance"""
    content = (
        "Here is the answer [source: abc123].\n"
        "More detail [sources: def456, abc123]."
    )
    assert _parse_source_ids(content) == ["abc123", "def456"]


def test_parse_source_ids_empty_when_none():
    """Returns an empty list when there are no citations"""
    assert _parse_source_ids("No citations here.") == []
