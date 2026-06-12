"""
Parser Service
Extracts text from PDFs, URLs, and notes
"""

import io
from typing import Tuple
import pdfplumber
import httpx
from bs4 import BeautifulSoup
from services.exceptions import PageLimitExceededError, ParseError


def parse_pdf(content: bytes) -> str:
    """
    Extract text from PDF bytes
    
    Args:
        content: PDF file content as bytes
        
    Returns:
        Concatenated text from all pages
        
    Raises:
        PageLimitExceededError: If PDF has more than 20 pages
        ParseError: If extraction fails or returns empty text
    """
    try:
        pdf_file = io.BytesIO(content)
        
        with pdfplumber.open(pdf_file) as pdf:
            # Check page count
            page_count = len(pdf.pages)
            if page_count > 20:
                raise PageLimitExceededError(f"PDF has {page_count} pages, maximum is 20")
            
            # Extract text from all pages
            text_parts = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            # Combine all pages
            full_text = "\n\n".join(text_parts)
            
            # Validate we got some text
            if not full_text or not full_text.strip():
                raise ParseError("PDF contains no extractable text")
            
            return full_text.strip()
            
    except PageLimitExceededError:
        raise
    except ParseError:
        raise
    except Exception as e:
        raise ParseError(f"Failed to parse PDF: {str(e)}")


def parse_url(url: str) -> Tuple[str, str]:
    """
    Fetch and extract text from a web page
    
    Args:
        url: URL to fetch
        
    Returns:
        Tuple of (text, page_title)
        
    Raises:
        ParseError: If page is unreachable or contains no text
    """
    try:
        # Fetch the page with timeout
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get page title
        title_tag = soup.find('title')
        page_title = title_tag.get_text().strip() if title_tag else url
        
        # Remove unwanted elements
        for element in soup.find_all(['nav', 'header', 'footer', 'script', 'style']):
            element.decompose()
        
        # Extract text from body
        body = soup.find('body')
        if body:
            text = body.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        
        # Validate we got some text
        if not text or not text.strip():
            raise ParseError("URL contains no extractable text")
        
        return text.strip(), page_title
        
    except httpx.TimeoutException:
        raise ParseError(f"Request to {url} timed out")
    except httpx.HTTPError as e:
        raise ParseError(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise ParseError(f"Failed to parse URL: {str(e)}")


def parse_note(content: str) -> str:
    """
    Process a plain text note
    
    Args:
        content: Note content
        
    Returns:
        Stripped content
        
    Raises:
        ParseError: If content is empty after stripping
    """
    text = content.strip()
    
    if not text:
        raise ParseError("Note content is empty")
    
    return text
