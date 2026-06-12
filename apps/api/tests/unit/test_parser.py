"""
Unit tests for parser service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import io
from services.parser import parse_pdf, parse_url, parse_note
from services.exceptions import PageLimitExceededError, ParseError


def test_parse_note_valid():
    """Valid note content is parsed successfully"""
    content = "This is a valid note with some content."
    result = parse_note(content)
    assert result == content


def test_parse_note_with_whitespace():
    """Note with surrounding whitespace is stripped"""
    content = "  \n  This is a note.  \n\n  "
    result = parse_note(content)
    assert result == "This is a note."


def test_parse_note_empty():
    """Empty note raises ParseError"""
    with pytest.raises(ParseError, match="Note content is empty"):
        parse_note("")


def test_parse_note_whitespace_only():
    """Whitespace-only note raises ParseError"""
    with pytest.raises(ParseError, match="Note content is empty"):
        parse_note("   \n\n\t   ")


@patch('services.parser.pdfplumber')
def test_parse_pdf_valid(mock_pdfplumber):
    """Valid PDF is parsed successfully"""
    # Mock PDF with 2 pages
    mock_page1 = Mock()
    mock_page1.extract_text.return_value = "Page 1 content"
    
    mock_page2 = Mock()
    mock_page2.extract_text.return_value = "Page 2 content"
    
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value.pages = [mock_page1, mock_page2]
    
    mock_pdfplumber.open.return_value = mock_pdf
    
    content = b"fake pdf bytes"
    result = parse_pdf(content)
    
    assert "Page 1 content" in result
    assert "Page 2 content" in result


@patch('services.parser.pdfplumber')
def test_parse_pdf_exceeds_page_limit(mock_pdfplumber):
    """PDF with more than 20 pages raises PageLimitExceededError"""
    # Mock PDF with 21 pages
    mock_pages = [Mock() for _ in range(21)]
    
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value.pages = mock_pages
    
    mock_pdfplumber.open.return_value = mock_pdf
    
    content = b"fake pdf bytes"
    
    with pytest.raises(PageLimitExceededError, match="21 pages"):
        parse_pdf(content)


@patch('services.parser.pdfplumber')
def test_parse_pdf_empty_text(mock_pdfplumber):
    """PDF with no extractable text raises ParseError"""
    mock_page = Mock()
    mock_page.extract_text.return_value = ""
    
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value.pages = [mock_page]
    
    mock_pdfplumber.open.return_value = mock_pdf
    
    content = b"fake pdf bytes"
    
    with pytest.raises(ParseError, match="no extractable text"):
        parse_pdf(content)


@patch('services.parser.httpx')
@patch('services.parser.BeautifulSoup')
def test_parse_url_valid(mock_bs, mock_httpx):
    """Valid URL is parsed successfully"""
    # Mock HTTP response
    mock_response = Mock()
    mock_response.text = "<html><head><title>Test Page</title></head><body><p>Content here</p></body></html>"
    mock_httpx.get.return_value = mock_response
    
    # Mock BeautifulSoup parsing
    mock_soup = Mock()
    mock_title = Mock()
    mock_title.get_text.return_value = "Test Page"
    mock_soup.find.return_value = mock_title
    
    mock_body = Mock()
    mock_body.get_text.return_value = "Content here"
    mock_soup.find_all.return_value = []  # No elements to remove
    
    # Setup proper mock behavior
    def find_side_effect(tag):
        if tag == 'title':
            return mock_title
        elif tag == 'body':
            return mock_body
        return None
    
    mock_soup.find.side_effect = find_side_effect
    mock_bs.return_value = mock_soup
    
    text, title = parse_url("https://example.com")
    
    assert title == "Test Page"
    assert "Content here" in text


@patch('services.parser.httpx')
def test_parse_url_timeout(mock_httpx):
    """URL that times out raises ParseError"""
    mock_httpx.get.side_effect = mock_httpx.TimeoutException("Timeout")
    
    with pytest.raises(ParseError, match="timed out"):
        parse_url("https://example.com")


@patch('services.parser.httpx')
def test_parse_url_http_error(mock_httpx):
    """URL with HTTP error raises ParseError"""
    mock_httpx.get.side_effect = mock_httpx.HTTPError("404 Not Found")
    
    with pytest.raises(ParseError, match="Failed to fetch URL"):
        parse_url("https://example.com")


@patch('services.parser.httpx')
@patch('services.parser.BeautifulSoup')
def test_parse_url_empty_content(mock_bs, mock_httpx):
    """URL with no text content raises ParseError"""
    mock_response = Mock()
    mock_response.text = "<html></html>"
    mock_httpx.get.return_value = mock_response
    
    mock_soup = Mock()
    mock_soup.find.return_value = None
    mock_soup.get_text.return_value = ""
    mock_soup.find_all.return_value = []
    mock_bs.return_value = mock_soup
    
    with pytest.raises(ParseError, match="no extractable text"):
        parse_url("https://example.com")
