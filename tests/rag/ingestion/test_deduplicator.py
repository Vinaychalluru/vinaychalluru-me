import numpy as np
import pytest
from rag._math import cosine_sim
from rag.ingestion.deduplicator import deduplicate
from rag.types import Chunk


def make_chunk(source: str, section: str = "test") -> Chunk:
    return Chunk(text=f"text from {source}", source=source, section=section)


def norm(v: list[float]) -> list[float]:
    arr = np.array(v)
    return (arr / np.linalg.norm(arr)).tolist()


def test_cosine_sim_identical_vectors():
    v = norm([1.0, 0.0, 0.0])
    assert abs(cosine_sim(v, v) - 1.0) < 1e-6


def test_cosine_sim_orthogonal_vectors():
    a = norm([1.0, 0.0, 0.0])
    b = norm([0.0, 1.0, 0.0])
    assert abs(cosine_sim(a, b)) < 1e-6


def test_no_duplicates_returns_all():
    chunks = [make_chunk("resume"), make_chunk("website")]
    embs = [norm([1.0, 0.0]), norm([0.0, 1.0])]
    kept_chunks, kept_embs = deduplicate(chunks, embs, threshold=0.97)
    assert len(kept_chunks) == 2


def test_near_duplicate_website_dropped_when_resume_exists():
    resume_chunk = Chunk(text="Solution Architect", source="resume", section="summary")
    website_chunk = Chunk(text="Solution Architect (slightly different)", source="website", section="hero")
    base = norm([1.0, 0.0, 0.0])
    near = norm([0.9999, 0.01, 0.0])
    kept_chunks, kept_embs = deduplicate([resume_chunk, website_chunk], [base, near], threshold=0.97)
    assert len(kept_chunks) == 1
    assert kept_chunks[0].source == "resume"


def test_resume_replaces_website_duplicate_when_website_seen_first():
    website_chunk = Chunk(text="Solution Architect", source="website", section="hero")
    resume_chunk = Chunk(text="Solution Architect", source="resume", section="summary")
    base = norm([1.0, 0.0, 0.0])
    near = norm([0.9999, 0.01, 0.0])
    kept_chunks, _ = deduplicate([website_chunk, resume_chunk], [base, near], threshold=0.97)
    assert len(kept_chunks) == 1
    assert kept_chunks[0].source == "resume"


def test_empty_input():
    kept_chunks, kept_embs = deduplicate([], [], threshold=0.97)
    assert kept_chunks == []
    assert kept_embs == []


def test_mismatched_lengths_raise():
    chunks = [make_chunk("resume")]
    embs = [norm([1.0, 0.0]), norm([0.0, 1.0])]
    with pytest.raises(ValueError, match="equal length"):
        deduplicate(chunks, embs)
