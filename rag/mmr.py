import numpy as np
from rag.types import Chunk


def _cosine(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a, dtype=float), np.array(b, dtype=float)
    denom = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    return float(np.dot(a_arr, b_arr) / denom) if denom > 0 else 0.0


def mmr_select(
    query_embedding: list[float],
    candidates: list[tuple[Chunk, float]],
    candidate_embeddings: list[list[float]],
    k: int,
    lambda_: float = 0.5,
) -> list[Chunk]:
    if not candidates:
        return []

    selected: list[int] = []
    remaining = list(range(len(candidates)))

    for _ in range(min(k, len(candidates))):
        best_idx: int | None = None
        best_score = float("-inf")

        for i in remaining:
            relevance = candidates[i][1]
            if not selected:
                redundancy = 0.0
            else:
                redundancy = max(
                    _cosine(candidate_embeddings[i], candidate_embeddings[j])
                    for j in selected
                )
            score = lambda_ * relevance - (1 - lambda_) * redundancy
            if score > best_score:
                best_score = score
                best_idx = i

        if best_idx is None:
            break

        selected.append(best_idx)
        remaining.remove(best_idx)

    return [candidates[i][0] for i in selected]
