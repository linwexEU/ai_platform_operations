from typing import Sequence, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.domain.interfaces.repositories.document import AbstractDocumentRepository
from app.domain.core.enums import DocumentStatus
from app.infrastructure.database.models import Document


class DocumentRepository(AbstractDocumentRepository): 
    def __init__(self, session: AsyncSession) -> None: 
        self.session = session
        
    async def create_document(
        self, 
        client_id: int, 
        filename: str, 
        mime_type: str, 
        size_bytes: int, 
        storage_key: str
    ) -> Document:
        document = Document(
            client_id=client_id,
            filename=filename,
            mime_type=mime_type,
            size_bytes=size_bytes,
            storage_key=storage_key
        )
        self.session.add(document)
        return document
    
    async def get_document_by_id(self, document_id: int) -> Optional[Document]:
        return await self.session.get(Document, document_id)
    
    async def get_documents(self, client_id: int, offset: int = 0, limit: int = 10) -> Sequence[Document]: 
        result = await self.session.execute(
            select(Document).where(Document.client_id == client_id).offset(offset).limit(limit)
        )
        return result.scalars().all()
    
    async def get_client_documents_count(self, client_id: int) -> int: 
        return await self.session.scalar(
            select(
                func.count()
            )
            .select_from(Document)
            .where(
                Document.client_id == client_id
            )
        )
    
    async def delete_document(self, document_id: int) -> None:
        await self.session.execute(
            delete(Document).where(Document.id == document_id)
        )

    async def mark_as_completed(self, document: Document) -> None:
        document.status = DocumentStatus.Completed
    