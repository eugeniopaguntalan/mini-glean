"""
Unit Tests for LLM Service
"""

import httpx
import pytest
from unittest.mock import patch, MagicMock
from openai import RateLimitError as OpenAIRateLimitError
from services.llm import (
    generate_answer,
    summarize,
    compare,
    get_client,
    get_chat_model,
)
from services.exceptions import LLMError, RateLimitError


def _openai_rate_limit_error() -> OpenAIRateLimitError:
    """Build a real openai.RateLimitError (needs an httpx response)."""
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx.Response(429, request=request)
    return OpenAIRateLimitError("rate limited", response=response, body=None)


def _mock_completion(content: str) -> MagicMock:
    """Build a mock chat-completion response with the given content."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = content
    return mock_response


def test_generate_answer_returns_content():
    """Should generate answer from question and context"""
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is the answer."
    
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(return_value=mock_response)
    
    with patch('services.llm.get_client', return_value=mock_client):
        answer = generate_answer("What is this?", "Context about the topic")
    
    assert answer == "This is the answer."


def test_generate_answer_uses_correct_model():
    """Should call OpenAI with gpt-4o model"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Answer"
    
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(return_value=mock_response)
    
    with patch('services.llm.get_client', return_value=mock_client):
        with patch('services.llm.settings') as mock_settings:
            mock_settings.LLM_MODEL = "gpt-4o"
            mock_settings.LLM_TEMPERATURE = 0.0
            
            generate_answer("Question", "Context")
            
            # Verify model parameter
            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs['model'] == "gpt-4o"


def test_generate_answer_uses_correct_temperature():
    """Should call OpenAI with temperature 0.0"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Answer"
    
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(return_value=mock_response)
    
    with patch('services.llm.get_client', return_value=mock_client):
        with patch('services.llm.settings') as mock_settings:
            mock_settings.LLM_MODEL = "gpt-4o"
            mock_settings.LLM_TEMPERATURE = 0.0
            
            generate_answer("Question", "Context")
            
            # Verify temperature parameter
            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs['temperature'] == 0.0


def test_generate_answer_raises_llm_error_on_failure():
    """Should raise LLMError when OpenAI call fails"""
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(
        side_effect=Exception("API Error")
    )
    
    with patch('services.llm.get_client', return_value=mock_client):
        with pytest.raises(LLMError) as exc_info:
            generate_answer("Question", "Context")
        
        assert "Failed to generate answer" in str(exc_info.value)


def test_get_client_returns_singleton():
    """Should return the same client instance on multiple calls"""
    # Reset singleton
    import services.llm
    services.llm._client = None
    
    with patch('services.llm.OpenAI') as mock_openai:
        client1 = get_client()
        client2 = get_client()
        
        # Should only create OpenAI client once
        assert mock_openai.call_count == 1
        assert client1 is client2
    
    # Reset singleton
    services.llm._client = None


def test_generate_answer_raises_rate_limit_error():
    """Should raise RateLimitError when OpenAI returns 429"""
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(
        side_effect=_openai_rate_limit_error()
    )

    with patch('services.llm.get_client', return_value=mock_client):
        with pytest.raises(RateLimitError) as exc_info:
            generate_answer("Question", "Context")

    assert "rate limited" in str(exc_info.value)


def test_summarize_returns_content():
    """Should return the summary text from the model"""
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(
        return_value=_mock_completion("A short summary.")
    )

    with patch('services.llm.get_client', return_value=mock_client):
        result = summarize("Some long document content.")

    assert result == "A short summary."


def test_summarize_raises_llm_error_on_failure():
    """Should raise LLMError when the summarize call fails"""
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(
        side_effect=Exception("API Error")
    )

    with patch('services.llm.get_client', return_value=mock_client):
        with pytest.raises(LLMError) as exc_info:
            summarize("content")

    assert "Failed to generate summary" in str(exc_info.value)


def test_summarize_raises_rate_limit_error():
    """Should raise RateLimitError when summarize is rate limited"""
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(
        side_effect=_openai_rate_limit_error()
    )

    with patch('services.llm.get_client', return_value=mock_client):
        with pytest.raises(RateLimitError):
            summarize("content")


def test_compare_returns_content():
    """Should return the comparison text from the model"""
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(
        return_value=_mock_completion("Doc A and Doc B differ in scope.")
    )

    with patch('services.llm.get_client', return_value=mock_client):
        result = compare("content a", "content b", "doc-a", "doc-b")

    assert result == "Doc A and Doc B differ in scope."


def test_compare_raises_llm_error_on_failure():
    """Should raise LLMError when the compare call fails"""
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(
        side_effect=Exception("API Error")
    )

    with patch('services.llm.get_client', return_value=mock_client):
        with pytest.raises(LLMError) as exc_info:
            compare("a", "b", "doc-a", "doc-b")

    assert "Failed to compare documents" in str(exc_info.value)


def test_compare_raises_rate_limit_error():
    """Should raise RateLimitError when compare is rate limited"""
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock(
        side_effect=_openai_rate_limit_error()
    )

    with patch('services.llm.get_client', return_value=mock_client):
        with pytest.raises(RateLimitError):
            compare("a", "b", "doc-a", "doc-b")


def test_get_chat_model_returns_singleton():
    """Should return the same ChatOpenAI instance on multiple calls"""
    import services.llm
    services.llm._chat_model = None

    with patch('services.llm.ChatOpenAI') as mock_chat:
        model1 = get_chat_model()
        model2 = get_chat_model()

        assert mock_chat.call_count == 1
        assert model1 is model2

    services.llm._chat_model = None
