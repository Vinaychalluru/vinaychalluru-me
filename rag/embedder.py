from __future__ import annotations
from abc import ABC, abstractmethod
import os
from openai import AzureOpenAI


class BaseEmbedder(ABC):
    dimension: int = 1536

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class AzureEmbedder(BaseEmbedder):
    dimension = 1536

    def __init__(self, endpoint: str, api_key: str, deployment: str):
        self._client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-01",
        )
        self._deployment = deployment

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(input=texts, model=self._deployment)
        return [item.embedding for item in response.data]


def make_embedder() -> AzureEmbedder:
    return AzureEmbedder(
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_KEY"],
        deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
    )
