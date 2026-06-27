import numpy as np
from rag.types import Chunk


def cosine_sim(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a, dtype=float), np.array(b, dtype=float)
    denom = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    return float(np.dot(a_arr, b_arr) / denom) if denom > 0 else 0.0


def deduplicate(
    chunks: list[Chunk],
    embeddings: list[list[float]],
    threshold: float = 0.97,
) -> tuple[list[Chunk], list[list[float]]]:
    if not chunks:
        return [], []

    if len(chunks) != len(embeddings):
        raise ValueError(
            f"chunks and embeddings must have equal length; "
            f"got chunks={len(chunks)}, embeddings={len(embeddings)}"
        )

    kept: list[int] = []

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        duplicate_of: int | None = None

        for j in kept:
            if cosine_sim(emb, embeddings[j]) >= threshold:
                duplicate_of = j
                break

        if duplicate_of is None:
            kept.append(i)
        elif chunk.source == "resume" and chunks[duplicate_of].source == "website":
            idx = kept.index(duplicate_of)
            kept[idx] = i

    return [chunks[i] for i in kept], [embeddings[i] for i in kept]
