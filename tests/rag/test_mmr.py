import numpy as np
from rag.mmr import mmr_select
from rag.types import Chunk


def norm(v: list[float]) -> list[float]:
    arr = np.array(v, dtype=float)
    return (arr / np.linalg.norm(arr)).tolist()


def make_chunk(label: str) -> Chunk:
    return Chunk(text=label, source="resume", section="test")


def test_returns_k_results():
    query = norm([1.0, 0.0, 0.0])
    candidates = [(make_chunk(f"c{i}"), 0.9 - i * 0.1) for i in range(5)]
    embs = [norm([1.0, i * 0.1, 0.0]) for i in range(5)]
    result = mmr_select(query, candidates, embs, k=3)
    assert len(result) == 3


def test_returns_fewer_when_candidates_exhausted():
    query = norm([1.0, 0.0, 0.0])
    candidates = [(make_chunk("c0"), 0.9), (make_chunk("c1"), 0.8)]
    embs = [norm([1.0, 0.0, 0.0]), norm([0.0, 1.0, 0.0])]
    result = mmr_select(query, candidates, embs, k=5)
    assert len(result) == 2


def test_empty_candidates_returns_empty():
    query = norm([1.0, 0.0, 0.0])
    result = mmr_select(query, [], [], k=5)
    assert result == []


def test_mmr_avoids_near_duplicates():
    query = norm([1.0, 0.0, 0.0])
    dup1 = make_chunk("dup1")
    dup2 = make_chunk("dup2")
    diverse = make_chunk("diverse")
    candidates = [(dup1, 0.95), (dup2, 0.94), (diverse, 0.80)]
    embs = [
        norm([1.0, 0.0, 0.0]),
        norm([0.999, 0.04, 0.0]),
        norm([0.0, 0.0, 1.0]),
    ]
    result = mmr_select(query, candidates, embs, k=2, lambda_=0.5)
    texts = [c.text for c in result]
    assert "dup1" in texts
    assert "diverse" in texts


def test_lambda_1_is_pure_relevance():
    query = norm([1.0, 0.0, 0.0])
    candidates = [
        (make_chunk("high_rel"), 0.95),
        (make_chunk("low_rel"), 0.50),
    ]
    embs = [norm([1.0, 0.0, 0.0]), norm([0.0, 1.0, 0.0])]
    result = mmr_select(query, candidates, embs, k=1, lambda_=1.0)
    assert result[0].text == "high_rel"
