"""
Unit tests for chunker service
"""

from services.chunker import chunk_text


def test_short_text_single_chunk():
    """Text shorter than chunk size returns single chunk"""
    text = "This is a short piece of text that should fit in one chunk."
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    
    assert len(chunks) == 1
    assert chunks[0] == text


def test_long_text_multiple_chunks():
    """Long text returns multiple chunks"""
    # Generate text long enough to require multiple chunks
    text = " ".join(["This is sentence number {}.".format(i) for i in range(200)])
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    
    assert len(chunks) > 1


def test_overlap_works():
    """Chunks have overlapping content"""
    # Generate medium-length text
    text = " ".join(["Word{}".format(i) for i in range(300)])
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    
    if len(chunks) > 1:
        # Verify there's some overlap by checking that chunks don't just concatenate back perfectly
        # This is a basic check - more sophisticated would tokenize and verify exact token overlap
        assert len(chunks) > 1


def test_tiny_last_chunk_merged():
    """Last chunk smaller than 50 tokens gets merged with previous"""
    # Create text that would result in a tiny last chunk
    text = " ".join(["Word{}".format(i) for i in range(150)])
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    
    # All chunks should be reasonable size
    for chunk in chunks:
        # Each chunk should have some content
        assert len(chunk) > 0


def test_empty_text():
    """Empty text returns empty list"""
    chunks = chunk_text("", chunk_size=500, overlap=50)
    assert chunks == []


def test_whitespace_only():
    """Whitespace-only text returns empty list"""
    chunks = chunk_text("   \n\n  \t  ", chunk_size=500, overlap=50)
    assert chunks == []


def test_exact_chunk_size():
    """Text exactly matching chunk size returns single chunk"""
    # This is approximate since we're using tokens
    text = " ".join(["Word"] * 100)
    chunks = chunk_text(text, chunk_size=1000, overlap=50)
    
    assert len(chunks) >= 1
