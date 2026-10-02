import asyncio
import pathlib
from typing import Sequence
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.entrypoints.tasks.document import task_delete_file_from_s3
from app.entrypoints.tasks.chunk import task_create_chunks
from app.infrastructure.object_storage.aws_s3 import ObjectStorage
from app.infrastructure.repositories.document import DocumentRepository
from app.infrastructure.uow.uow import UnitOfWork
from app.infrastructure.database.models import Document
from app.domain.core.config import settings
from app.domain.exceptions.document import (
    InvalidDocumentMimeTypeError, 
    ExceededDocumentSizeError, 
    DocumentNotFoundError
)


class DocumentService: 
    def __init__(self, session: AsyncSession, object_storage: ObjectStorage) -> None: 
        self.repo = DocumentRepository(session)
        self.object_storage = object_storage
        
    async def create_document(
        self, 
        client_id: int, 
        filename: str, 
        mime_type: str, 
        size_bytes: int
    ) -> tuple[Document, str]: 
        # Validate mime type
        if mime_type != "application/pdf": 
            raise InvalidDocumentMimeTypeError()
        
        # Validate size
        if size_bytes > 10 ** 7:
            raise ExceededDocumentSizeError()
        
        # Add document to the primary storage & Generate upload_url
        suffix = pathlib.Path(filename).suffix.lower()
        storage_key = f"docs/{client_id}/{uuid.uuid4().hex}{suffix}"
        
        async def document_wrapper() -> Document:
            async with UnitOfWork() as uow: 
                document = await uow.document_repo.create_document(
                    client_id, 
                    filename, 
                    mime_type, 
                    size_bytes, 
                    storage_key
                )
                return document
            
        document, url = await asyncio.gather(
            document_wrapper(), 
            self.object_storage.generate_upload_link(storage_key) 
        )

        return document, url
    
    async def get_client_documents(self, client_id: int, offset: int, limit: int) -> tuple[Sequence[Document], int]: 
        documents, total_count = await asyncio.gather(
            self.repo.get_documents(client_id, offset, limit), 
            self.repo.get_client_documents_count(client_id)
        )
        return documents, total_count

    async def mark_as_completed(self, client_id: int, document_id: int) -> None:
        try:
            async with UnitOfWork() as uow: 
                document = await uow.document_repo.get_document_by_id(document_id) 
                
                if document is None or document.client_id != client_id: 
                    raise DocumentNotFoundError()

                await uow.document_repo.mark_as_completed(document)
                
                # Create job for background chunking
                idempotency_key = f"{document.storage_key}:v{settings.CHUNKING_VERSION}:{settings.OLLAMA_EMBEDDING_MODEL}:{settings.EMBEDDING_DIMENSION}"
                
                job = await uow.ingestion_job_repo.create_job(
                    document.id, 
                    idempotency_key, 
                    f"v{settings.CHUNKING_VERSION}", 
                    settings.OLLAMA_EMBEDDING_MODEL, 
                    settings.EMBEDDING_DIMENSION
                )
                
                # Add this job to the outbox table
                await uow.outbox_repo.create_event(job.id, "CREATE_CHUNKS")
        except IntegrityError:
            pass

    async def delete_document(self, client_id: int, document_id: int) -> None: 
        # Delete from primary storage
        async with UnitOfWork() as uow: 
            document = await uow.document_repo.get_document_by_id(document_id)
            
            if document is None or document.client_id != client_id: 
                raise DocumentNotFoundError()
            
            await uow.document_repo.delete_document(document_id)
            
            # Delete chunks
            await uow.chunk_repo.delete_chunks(document.id)
        
        # Delete from object storage
        task_delete_file_from_s3.delay(document.storage_key)
            