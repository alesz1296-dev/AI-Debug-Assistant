from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from app.schemas.debug import CollectionName


@dataclass(frozen=True)
class KnowledgeRecord:
    collection: CollectionName
    title: str
    source: str
    text: str
    tags: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

