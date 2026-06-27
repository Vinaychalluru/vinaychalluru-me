import uuid
import tiktoken
from rag.types import Chunk

_ENC = tiktoken.get_encoding("cl100k_base")


def chunk_text(
    text: str,
    source: str,
    section: str,
    chunk_size: int = 512,
    overlap: int = 50,
) -> list[Chunk]:
    if chunk_size <= 0 or overlap >= chunk_size:
        raise ValueError(
            f"chunk_size must be positive and greater than overlap; "
            f"got chunk_size={chunk_size}, overlap={overlap}"
        )
    text = text.strip()
    if not text:
        return []

    tokens = _ENC.encode(text)
    if not tokens:
        return []

    chunks: list[Chunk] = []
    start = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text_str = _ENC.decode(chunk_tokens).strip()

        if chunk_text_str:
            chunks.append(Chunk(
                text=chunk_text_str,
                source=source,
                section=section,
                chunk_id=str(uuid.uuid4()),
                token_count=len(chunk_tokens),
            ))

        if end == len(tokens):
            break

        start += chunk_size - overlap

    return chunks
