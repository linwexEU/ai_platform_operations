from abc import ABC, abstractmethod
from typing import Sequence, Optional

from app.infrastructure.database.models import Document


class AbstractDocumentRepository(ABC): 
    @abstractmethod
    async def create_document(
        self, 
        client_id: int,
        filename: str, 
        mime_type: str, 
        size_bytes: int,
        storage_key: str
    ) -> Document: ...
    
    @abstractmethod
    async def get_documents(self, client_id: int) -> Sequence[Document]: ...
    
    @abstractmethod
    async def get_document_by_id(self, document_id: int) -> Optional[Document]: ...
    
    @abstractmethod
    async def delete_document(self, document: Document) -> None: ...

    @abstractmethod
    async def mark_as_completed(self, document: Document) -> None: ...
    