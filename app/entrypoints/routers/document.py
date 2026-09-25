from fastapi import APIRouter, HTTPException, status

from app.entrypoints.dependencies.auth import CurrActivatedClient
from app.entrypoints.dependencies.document import DocumentServiceDep
from app.domain.exceptions.document import (
    InvalidDocumentMimeTypeError, 
    ExceededDocumentSizeError, 
    DocumentNotFoundError
)
from app.entrypoints.schemas.document import (
    InitDocumentRequest, 
    InitDocumentResponse, 
    ClientDocumentsResponse
)

router = APIRouter()


@router.post("/init")
async def create_document(
    payload: InitDocumentRequest, 
    curr_client: CurrActivatedClient, 
    service: DocumentServiceDep
) -> InitDocumentResponse: 
    try:
        document, url = await service.create_document(curr_client.id, payload.filename, payload.mime_type, payload.size_bytes)
    except InvalidDocumentMimeTypeError: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document's mime type error")
    except ExceededDocumentSizeError: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large error")
    return InitDocumentResponse(
        document_id=document.id, 
        upload_url=url, 
        storage_key=document.storage_key
    )
    
    
@router.get("/")
async def get_clients_documents(
    curr_client: CurrActivatedClient, 
    service: DocumentServiceDep, 
    offset: int = 0, 
    limit: int = 10
) -> ClientDocumentsResponse: 
    documents, total_count = await service.get_client_documents(curr_client.id, offset, limit) 
    return ClientDocumentsResponse.from_orm(documents, total_count)


@router.put("/{document_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def mark_document_as_completed(
    document_id: int, 
    curr_client: CurrActivatedClient, 
    service: DocumentServiceDep
) -> None: 
    try:
        await service.mark_as_completed(curr_client.id, document_id) 
    except DocumentNotFoundError: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int, 
    curr_client: CurrActivatedClient, 
    service: DocumentServiceDep
) -> None: 
    try: 
        await service.delete_document(curr_client.id, document_id)
    except DocumentNotFoundError: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found") 
