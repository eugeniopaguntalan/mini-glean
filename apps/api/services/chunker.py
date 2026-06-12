"""
Chunker Service
Splits text into token-sized chunks with overlap
"""

import tiktoken
from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into chunks of specified token size with overlap
    
    Args:
        text: Text to chunk
        chunk_size: Maximum tokens per chunk (default: 500)
        overlap: Tokens to overlap between chunks (default: 50)
        
    Returns:
        List of text chunks
    """
    # Get the tokenizer (same as OpenAI models)
    encoding = tiktoken.get_encoding("cl100k_base")
    
    # Tokenize the text
    tokens = encoding.encode(text)
    
    # If text is shorter than chunk size, return as single chunk
    if len(tokens) <= chunk_size:
        return [text] if text.strip() else []
    
    chunks = []
    start_idx = 0
    
    while start_idx < len(tokens):
        # Get chunk of tokens
        end_idx = start_idx + chunk_size
        chunk_tokens = tokens[start_idx:end_idx]
        
        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens)
        
        # Try to preserve sentence boundaries
        # If not at the end and chunk doesn't end with sentence boundary, try to cut at last sentence
        if end_idx < len(tokens) and not chunk_text.rstrip().endswith(('.', '!', '?', '\n')):
            # Find last sentence boundary in chunk
            for delim in ['. ', '! ', '? ', '\n']:
                last_delim = chunk_text.rfind(delim)
                if last_delim > len(chunk_text) * 0.5:  # Only if it's not too early
                    chunk_text = chunk_text[:last_delim + 1].rstrip()
                    # Re-encode to get actual token count for this adjusted chunk
                    chunk_tokens = encoding.encode(chunk_text)
                    break
        
        chunks.append(chunk_text.strip())
        
        # Move start index forward, accounting for overlap
        start_idx += len(chunk_tokens) - overlap
        
        # Ensure we make progress even if chunk is very small
        if len(chunk_tokens) <= overlap:
            start_idx = end_idx
    
    # Merge last chunk if it's too small (< 50 tokens)
    if len(chunks) > 1:
        last_chunk_tokens = encoding.encode(chunks[-1])
        if len(last_chunk_tokens) < 50:
            # Merge with previous chunk
            merged = chunks[-2] + " " + chunks[-1]
            chunks = chunks[:-2] + [merged]
    
    return chunks
