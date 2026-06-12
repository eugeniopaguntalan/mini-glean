"""
LLM Service
Single entry point for all OpenAI chat completions
"""

from typing import Optional
from openai import OpenAI
from config import settings
from prompts.qa import QA_SYSTEM_PROMPT
from services.exceptions import LLMError


# Singleton client instance
_client: Optional[OpenAI] = None


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
        
    except Exception as e:
        raise LLMError(f"Failed to generate answer: {str(e)}")
