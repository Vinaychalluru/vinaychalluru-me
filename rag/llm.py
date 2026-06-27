from __future__ import annotations
import os
from abc import ABC, abstractmethod
from typing import AsyncGenerator
from anthropic import AsyncAnthropic


class BaseLLM(ABC):
    @abstractmethod
    async def stream(self, messages: list[dict]) -> AsyncGenerator[str, None]: ...


class ClaudeClient(BaseLLM):
    def __init__(self, api_key: str, model: str, max_tokens: int = 1024):
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    async def stream(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        system = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_messages = [m for m in messages if m["role"] != "system"]
        kwargs: dict = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "messages": user_messages,
        }
        if system:
            kwargs["system"] = system
        async with self._client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text


def make_llm() -> ClaudeClient:
    return ClaudeClient(
        api_key=os.environ["CLAUDE_API_KEY"],
        model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6"),
        max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "1024")),
    )
