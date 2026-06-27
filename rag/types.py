from dataclasses import dataclass, field
import uuid


@dataclass
class Chunk:
    text: str
    source: str
    section: str
    chunk_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    token_count: int = 0
