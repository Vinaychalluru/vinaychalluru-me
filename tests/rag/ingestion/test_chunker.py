import pytest
from rag.ingestion.chunker import chunk_text
from rag.types import Chunk


def test_chunk_text_produces_multiple_chunks():
    text = "Vinay Kumar Challuru. " * 100
    chunks = chunk_text(text, source="resume", section="summary", chunk_size=50, overlap=10)
    assert len(chunks) > 1
    for c in chunks:
        assert isinstance(c, Chunk)
        assert c.source == "resume"
        assert c.section == "summary"
        assert c.token_count > 0
        assert len(c.chunk_id) == 36


def test_short_text_produces_single_chunk():
    text = "Vinay is a Solution Architect."
    chunks = chunk_text(text, source="website", section="hero", chunk_size=512, overlap=50)
    assert len(chunks) == 1
    assert "Vinay" in chunks[0].text


def test_overlap_ensures_content_continuity():
    text = " ".join(f"word{i}" for i in range(200))
    chunks = chunk_text(text, source="resume", section="test", chunk_size=50, overlap=20)
    assert len(chunks) >= 2
    last_words_chunk0 = chunks[0].text.split()[-5:]
    first_words_chunk1 = chunks[1].text.split()[:25]
    overlap_found = any(w in first_words_chunk1 for w in last_words_chunk0)
    assert overlap_found


def test_empty_text_returns_empty_list():
    assert chunk_text("", source="resume", section="test") == []


def test_whitespace_only_returns_empty_list():
    assert chunk_text("   \n\n  ", source="resume", section="test") == []


def test_invalid_overlap_raises():
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        chunk_text("some text", source="resume", section="test", chunk_size=50, overlap=50)
