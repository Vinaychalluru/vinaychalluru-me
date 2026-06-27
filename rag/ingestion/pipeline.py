import asyncio
import logging
import time
from pathlib import Path

from rag.types import Chunk
from rag.ingestion.loader import fetch_pdf_text, scrape_website_sections
from rag.ingestion.chunker import chunk_text
from rag.ingestion.deduplicator import deduplicate
from rag.embedder import BaseEmbedder
from rag.vector_store import BaseVectorStore

logger = logging.getLogger(__name__)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


async def run_ingest(
    pdf_path: Path,
    html_path: Path,
    embedder: BaseEmbedder,
    store: BaseVectorStore,
) -> dict:
    start = time.time()

    logger.info("Reading resume PDF from %s", pdf_path)
    pdf_text = await fetch_pdf_text(pdf_path)

    logger.info("Parsing website template from %s", html_path)
    website_sections = await scrape_website_sections(html_path)

    all_chunks: list[Chunk] = []

    resume_chunks = chunk_text(pdf_text, source="resume", section="resume",
                               chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    all_chunks.extend(resume_chunks)

    for sec in website_sections:
        site_chunks = chunk_text(sec["text"], source="website", section=sec["section"],
                                 chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        all_chunks.extend(site_chunks)

    texts = [c.text for c in all_chunks]
    embeddings = await asyncio.to_thread(embedder.embed_texts, texts)

    unique_chunks, unique_embeddings = deduplicate(all_chunks, embeddings, threshold=0.97)
    logger.info("After dedup: %d unique chunks (dropped %d)",
                len(unique_chunks), len(all_chunks) - len(unique_chunks))

    await store.delete_all()
    await store.upsert(unique_chunks, unique_embeddings)

    elapsed = round(time.time() - start, 2)
    return {
        "total_chunks": len(unique_chunks),
        "resume_chunks": len(resume_chunks),
        "website_sections": len(website_sections),
        "elapsed_seconds": elapsed,
    }
