from fastapi import APIRouter, HTTPException, status

from app.entrypoints.dependencies.auth import CurrActivatedClient
from app.entrypoints.dependencies.session import SessionServiceDep
from app.domain.exceptions.session import SessionIsNotFoundError
from app.domain.exceptions.session_document import DocumentAlreadyAttachedError
from app.domain.exceptions.document import DocumentNotFoundError
from app.entrypoints.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse, 
    GetSessionsChatResponse, 
    SSession, 
    SSessionFull,
    UpdateSessionRequest,
    UpdateSessionResponse
)
from app.entrypoints.schemas.message import (
    CreateMessageResponse,
    GetMessagesResponse
)

router = APIRouter()


@router.post("/")
async def create_session_chat(
    curr_client: CurrActivatedClient, 
    payload: CreateSessionRequest, 
    service: SessionServiceDep
) -> CreateSessionResponse:
    session_chat = await service.create_session_chat(curr_client.id, payload.name) 
    return CreateSessionResponse.from_orm(session_chat)


@router.get("/")
async def get_sessions_chat(
    curr_client: CurrActivatedClient, 
    service: SessionServiceDep, 
    offset: int = 0, 
    limit: int = 10
) -> GetSessionsChatResponse: 
    sessions = await service.get_clients_sessions_chat(curr_client.id, offset, limit)
    total_count = await service.get_total_count_clients_sessions(curr_client.id)
    return GetSessionsChatResponse(
        sessions=[SSession.from_orm(session) for session in sessions], 
        total_count=total_count
    )


@router.get("/{session_id}")
async def get_session_chat(session_id: int, curr_client: CurrActivatedClient, service: SessionServiceDep) -> SSessionFull: 
    try:
        session = await service.get_session_chat_by_session_id(curr_client.id, session_id)
        return SSessionFull.from_orm(session)
    except SessionIsNotFoundError: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session is not found")


@router.put("/{session_id}")
async def update_session_chat(
    session_id: int,
    payload: UpdateSessionRequest, 
    curr_client: CurrActivatedClient, 
    service: SessionServiceDep
) -> UpdateSessionResponse: 
    try:
        session = await service.update_session_chat(curr_client.id, session_id, payload.name) 
        return UpdateSessionResponse.from_orm(session)
    except SessionIsNotFoundError: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session is not found")


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session_chat(session_id: int, curr_client: CurrActivatedClient, service: SessionServiceDep) -> None: 
    try: 
        await service.delete_session_chat(curr_client.id, session_id)
    except SessionIsNotFoundError: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session is not found") 


@router.post("/{session_id}/attach/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def attach_document(
    session_id: int, 
    document_id: int, 
    curr_client: CurrActivatedClient, 
    service: SessionServiceDep
) -> None:
    try: 
        await service.attach_document(curr_client.id, session_id, document_id) 
    except SessionIsNotFoundError: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session is not found")
    except DocumentNotFoundError: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except DocumentAlreadyAttachedError: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document already attached")


@router.post("/{session_id}/detach/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_document(
    session_id: int, 
    document_id: int, 
    curr_client: CurrActivatedClient, 
    service: SessionServiceDep
) -> None: 
    try: 
        await service.detach_document(curr_client.id, session_id, document_id) 
    except SessionIsNotFoundError: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session is not found")
    except DocumentNotFoundError: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


@router.post("/{session_id}/message", status_code=status.HTTP_204_NO_CONTENT)
async def save_message(
    session_id: int, 
    payload: CreateMessageResponse,
    curr_client: CurrActivatedClient, 
    service: SessionServiceDep
) -> None: 
    await service.save_message(curr_client.id, session_id, payload.sender, payload.text) 


@router.get("/{session_id}/message")
async def get_messages(
    session_id: int, 
    curr_client: CurrActivatedClient, 
    service: SessionServiceDep,
    offset: int = 0, 
    limit: int = 50
) -> GetMessagesResponse: 
    messages, total = await service.get_messages(curr_client.id, session_id, offset, limit)
    return GetMessagesResponse.from_orm(messages, total)


@router.get("/{session_id}/stream")
async def stream(session_id: int, curr_client: CurrActivatedClient): 
    pass 
