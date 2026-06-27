from __future__ import annotations
import logging
import os
from abc import ABC, abstractmethod
from typing import Literal

from azure.search.documents.aio import SearchClient as AsyncSearchClient
from azure.search.documents.indexes.aio import SearchIndexClient as AsyncSearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

from rag.types import Chunk

_logger = logging.getLogger(__name__)

VectorStoreStatus = Literal["ok", "not_ingested", "unreachable"]


class BaseVectorStore(ABC):
    @abstractmethod
    async def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None: ...

    @abstractmethod
    async def search(self, query_embedding: list[float], k: int) -> list[tuple[Chunk, float, list[float]]]: ...

    @abstractmethod
    async def health_check(self) -> VectorStoreStatus: ...

    @abstractmethod
    async def delete_all(self) -> None: ...


class AzureSearchStore(BaseVectorStore):
    def __init__(self, endpoint: str, api_key: str, index_name: str, vector_size: int = 1536):
        credential = AzureKeyCredential(api_key)
        self._search_client = AsyncSearchClient(endpoint, index_name, credential)
        self._index_client = AsyncSearchIndexClient(endpoint, credential)
        self._index_name = index_name
        self._vector_size = vector_size

    def _build_index_schema(self):
        from azure.search.documents.indexes.models import (
            SearchIndex, SearchField, SearchFieldDataType,
            SimpleField, SearchableField,
            VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
        )
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SimpleField(name="chunk_id", type=SearchFieldDataType.String),
            SearchableField(name="text", type=SearchFieldDataType.String),
            SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="section", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="token_count", type=SearchFieldDataType.Int32),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                retrievable=True,  # required for MMR — Azure Search won't return vectors without this
                vector_search_dimensions=self._vector_size,
                vector_search_profile_name="default-profile",
            ),
        ]
        vector_search = VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="default-algo")],
            profiles=[VectorSearchProfile(name="default-profile", algorithm_configuration_name="default-algo")],
        )
        return SearchIndex(name=self._index_name, fields=fields, vector_search=vector_search)

    async def _ensure_index(self) -> None:
        try:
            await self._index_client.get_index(self._index_name)
        except ResourceNotFoundError:
            await self._index_client.create_or_update_index(self._build_index_schema())

    async def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        await self._ensure_index()
        docs = [
            {
                "id": str(i),
                "chunk_id": c.chunk_id,
                "text": c.text,
                "source": c.source,
                "section": c.section,
                "token_count": c.token_count,
                "embedding": emb,
            }
            for i, (c, emb) in enumerate(zip(chunks, embeddings))
        ]
        await self._search_client.upload_documents(docs)

    async def search(self, query_embedding: list[float], k: int) -> list[tuple[Chunk, float, list[float]]]:
        from azure.search.documents.models import VectorizedQuery
        try:
            results = self._search_client.search(
                search_text=None,
                vector_queries=[
                    VectorizedQuery(vector=query_embedding, k_nearest_neighbors=k, fields="embedding")
                ],
                select=["id", "chunk_id", "text", "source", "section", "token_count", "embedding"],
            )
            return [
                (
                    Chunk(
                        text=r["text"],
                        source=r["source"],
                        section=r["section"],
                        chunk_id=r["chunk_id"],
                        token_count=r["token_count"],
                    ),
                    r["@search.score"],
                    list(r["embedding"]),
                )
                async for r in results
            ]
        except ResourceNotFoundError:
            _logger.warning("Azure Search index '%s' not found — run POST /api/ingest first", self._index_name)
            return []
        except HttpResponseError as exc:
            _logger.error("Azure Search query failed: %s %s", exc.status_code, exc.message)
            return []

    async def health_check(self) -> VectorStoreStatus:
        try:
            await self._index_client.get_index(self._index_name)
            return "ok"
        except ResourceNotFoundError:
            return "not_ingested"
        except Exception:
            return "unreachable"

    async def delete_all(self) -> None:
        try:
            await self._index_client.delete_index(self._index_name)
        except Exception:
            pass


def make_vector_store(vector_size: int = 1536) -> AzureSearchStore:
    return AzureSearchStore(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        api_key=os.environ["AZURE_SEARCH_KEY"],
        index_name=os.environ.get("AZURE_SEARCH_INDEX", "vc-profile"),
        vector_size=vector_size,
    )
