"""
Unit Tests for LLM Service
"""

import pytest
from unittest.mock import patch, MagicMock
from services.llm import generate_answer, get_client
from services.exceptions import LLMError


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
