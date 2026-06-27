import asyncio
import time


class SessionStore:
    def __init__(self, ttl_seconds: int = 3600):
        self._sessions: dict[str, list[dict]] = {}
        self._timestamps: dict[str, float] = {}
        self._ttl = ttl_seconds
        self._lock = asyncio.Lock()

    async def get_messages(self, session_id: str) -> list[dict]:
        async with self._lock:
            self._purge_expired()
            if session_id not in self._sessions:
                return []
            self._timestamps[session_id] = time.time()
            return list(self._sessions[session_id])

    async def append_messages(self, session_id: str, messages: list[dict]) -> None:
        async with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = []
                self._timestamps[session_id] = time.time()
            self._sessions[session_id].extend(messages)
            self._timestamps[session_id] = time.time()

    async def clear(self, session_id: str) -> None:
        async with self._lock:
            self._sessions.pop(session_id, None)
            self._timestamps.pop(session_id, None)

    def _purge_expired(self) -> None:
        now = time.time()
        expired = [sid for sid, ts in self._timestamps.items() if now - ts > self._ttl]
        for sid in expired:
            self._sessions.pop(sid, None)
            self._timestamps.pop(sid, None)
