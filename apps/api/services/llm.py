"""
LLM Service
Single entry point for all OpenAI chat completions
"""

from typing import Optional
from openai import OpenAI, RateLimitError as OpenAIRateLimitError
from langchain_openai import ChatOpenAI
from config import settings
from prompts.qa import QA_SYSTEM_PROMPT
from prompts.summarize import SUMMARIZE_PROMPT
from prompts.compare import COMPARE_PROMPT
from services.exceptions import LLMError, RateLimitError


# Singleton client instance
_client: Optional[OpenAI] = None
_chat_model: Optional[ChatOpenAI] = None


def get_client() -> OpenAI:
    """
    Get or create the OpenAI client singleton
    
    Returns:
        OpenAI client instance
    """
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def get_chat_model() -> ChatOpenAI:
    """
    Get or create the LangChain ChatOpenAI model singleton
    
    This is the single entry point for the LangChain chat model used by
    the agent. The OpenAI client is never instantiated outside this module.
    
    Returns:
        ChatOpenAI instance configured with the project model and temperature
    """
    global _chat_model
    if _chat_model is None:
        _chat_model = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
        )
    return _chat_model


def generate_answer(question: str, context: str) -> str:
    """
    Generate an answer to a question using the provided context
    
    Args:
        question: The user's question
        context: Retrieved context chunks formatted as string
        
    Returns:
        The assistant's answer as a string
        
    Raises:
        LLMError: If the OpenAI API call fails
    """
    try:
        client = get_client()
        
        # Build the full prompt with context
        system_message = QA_SYSTEM_PROMPT.format(context=context)
        
        # Call OpenAI chat completion
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": question}
            ]
        )
        
        # Extract and return the answer
        return response.choices[0].message.content or ""
        
    except OpenAIRateLimitError as e:
        raise RateLimitError(f"LLM service rate limited: {str(e)}")
    except Exception as e:
        raise LLMError(f"Failed to generate answer: {str(e)}")


def summarize(content: str) -> str:
    """
    Generate a concise summary of document content
    
    Args:
        content: The full document content to summarize
        
    Returns:
        The summary as a string
        
    Raises:
        LLMError: If the OpenAI API call fails
    """
    try:
        client = get_client()
        
        prompt = SUMMARIZE_PROMPT.format(content=content)
        
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content or ""
        
    except OpenAIRateLimitError as e:
        raise RateLimitError(f"LLM service rate limited: {str(e)}")
    except Exception as e:
        raise LLMError(f"Failed to generate summary: {str(e)}")


def compare(content_a: str, content_b: str, doc_id_a: str, doc_id_b: str) -> str:
    """
    Compare two documents and return similarities and differences
    
    Args:
        content_a: Full content of the first document
        content_b: Full content of the second document
        doc_id_a: ID of the first document
        doc_id_b: ID of the second document
        
    Returns:
        The comparison as a string
        
    Raises:
        LLMError: If the OpenAI API call fails
    """
    try:
        client = get_client()
        
        prompt = COMPARE_PROMPT.format(
            content_a=content_a,
            content_b=content_b,
            doc_id_a=doc_id_a,
            doc_id_b=doc_id_b
        )
        
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content or ""
        
    except OpenAIRateLimitError as e:
        raise RateLimitError(f"LLM service rate limited: {str(e)}")
    except Exception as e:
        raise LLMError(f"Failed to compare documents: {str(e)}")
