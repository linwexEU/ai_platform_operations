from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.domain.interfaces.repositories.chunk import AbstractChunkRepository
from app.infrastructure.database.models import Chunk, Document, SessionDocument


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
    
    async def retrieve_similar(
        self,
        session_id: int,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> Sequence[Chunk]:
        result = await self.session.execute(
            select(Chunk)
            .join(Document, Document.id == Chunk.document_id)
            .join(
                SessionDocument,
                SessionDocument.document_id == Document.id,
            )
            .where(SessionDocument.session_id == session_id)
            .order_by(Chunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        return result.scalars().all()
    