from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.domain.interfaces.repositories.chunk import AbstractChunkRepository
from app.infrastructure.database.models import Chunk


class ChunkRepository(AbstractChunkRepository): 
    def __init__(self, session: AsyncSession) -> None: 
        self.session = session

    async def create_chunk(self, document_id: int, chunk_index: int, text: str, embedding: list[float]) -> Chunk:
        chunk = Chunk(
            document_id=document_id,
            chunk_index=chunk_index,
            text=text,
            embedding=embedding
        )
        self.session.add(chunk) 
        return chunk
    
    async def get_document_chunks(self, document_id) -> Sequence[Chunk]:
        result = await self.session.execute(
            select(Chunk)
            .where(
                Chunk.document_id == document_id
            )
        )
        return result.scalars().all()
    
    async def delete_chunks(self, document_id: int) -> None:
        await self.session.execute(
            delete(Chunk)
            .where(
                Chunk.document_id == document_id
            )
        )
    