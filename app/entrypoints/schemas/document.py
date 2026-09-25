from datetime import datetime
from typing import Sequence

from pydantic import BaseModel

from app.domain.core.enums import DocumentStatus
from app.infrastructure.database.models import Document


class InitDocumentRequest(BaseModel): 
    filename: str
    mime_type: str
    size_bytes: int
    
    
class InitDocumentResponse(BaseModel): 
    document_id: int
    upload_url: str
    storage_key: str


class SDocument(BaseModel): 
    id: int
    filename: str
    mime_type: str
    size_bytes: int
    storage_key: str
    status: DocumentStatus
    created_at: datetime
    
    @staticmethod
    def from_orm(document: Document) -> "SDocument": 
        return SDocument(
            id=document.id, 
            filename=document.filename,
            mime_type=document.mime_type,
            size_bytes=document.size_bytes,
            storage_key=document.storage_key,
            status=document.status,
            created_at=document.created_at
        )


class ClientDocumentsResponse(BaseModel): 
    documents: list[SDocument]
    total_count: int

    @staticmethod
    def from_orm(documents: Sequence[Document], total_count: int) -> "ClientDocumentsResponse": 
        documents = [SDocument.from_orm(document) for document in documents]
        return ClientDocumentsResponse(
            documents=documents, 
            total_count=total_count
        )
    