from abc import ABC, abstractmethod
from typing import Sequence

from app.infrastructure.database.models import Chunk


class AbstractChunkRepository(ABC):
    @abstractmethod
    async def create_chunk(self, document_id: int, chunk_index: int, text: str, embedding: list[float]) -> Chunk: ...
    
    @abstractmethod 
    async def get_document_chunks(self, document_id: int) -> Sequence[Chunk]: ...
    
    @abstractmethod
    async def delete_chunks(self, document_id: int) -> None: ...
