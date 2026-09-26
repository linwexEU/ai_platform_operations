from typing import Sequence, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.domain.exceptions.document import DocumentNotFoundError
from app.domain.exceptions.session import SessionIsNotFoundError
from app.domain.exceptions.session_document import DocumentAlreadyAttachedError
from app.infrastructure.database.models import Session
from app.infrastructure.repositories.session import SessionRepository
from app.infrastructure.uow.uow import UnitOfWork


class SessionService: 
    def __init__(self, session: AsyncSession) -> None:
        self.repo = SessionRepository(session)
        
    async def create_session_chat(self, client_id: int, name: str) -> Session: 
        async with UnitOfWork() as uow: 
            session_chat = await uow.session_repo.create_session_chat(client_id, name)
        return session_chat 
    
    async def get_clients_sessions_chat(self, client_id: int, offset: int = 0, limit: int = 10) -> Sequence[Session]: 
        return await self.repo.get_client_sessions(client_id, offset, limit)
    
    async def get_total_count_clients_sessions(self, client_id: int) -> int: 
        return await self.repo.get_total_count_clients_sessions(client_id)

    async def get_session_chat_by_session_id(self, client_id: int, session_id: int) -> Optional[Session]: 
        session_chat = await self.repo.get_session_chat_by_id(session_id)
        
        if session_chat is None: 
            raise SessionIsNotFoundError()
        
        if session_chat.client_id != client_id: 
            raise SessionIsNotFoundError()
        
        return session_chat
    
    async def update_session_chat(self, client_id: int, session_id: int, name: str) -> Session: 
        async with UnitOfWork() as uow: 
            session_chat = await uow.session_repo.get_session_chat_by_id(session_id)
                        
            if session_chat is None: 
                raise SessionIsNotFoundError()
            
            if session_chat.client_id != client_id: 
                raise SessionIsNotFoundError()
            
            await uow.session_repo.update_session_chat(session_chat, name)
        
        return session_chat
    
    async def delete_session_chat(self, client_id: int, session_id: int) -> None: 
        async with UnitOfWork() as uow: 
            session_chat = await uow.session_repo.get_session_chat_by_id(session_id)
            
            if session_chat is None: 
                raise SessionIsNotFoundError()
            
            if session_chat.client_id != client_id: 
                raise SessionIsNotFoundError()
            
            await uow.session_repo.delete_session_chat(session_id)
    
    async def attach_document(self, client_id: int, session_id: int, document_id: int) -> None: 
        try:
            async with UnitOfWork() as uow: 
                await self._validate_session_and_document(client_id, session_id, document_id, uow)
                await uow.session_document_repo.attach_document_to_session(session_id, document_id)
        except IntegrityError: 
            raise DocumentAlreadyAttachedError()
            
    async def detach_document(self, client_id: int, session_id: int, document_id: int) -> None: 
        async with UnitOfWork() as uow: 
            await self._validate_session_and_document(client_id, session_id, document_id, uow)
            await uow.session_document_repo.detach_document_from_session(session_id, document_id)

    async def _validate_session_and_document(
        self, 
        client_id: int, 
        session_id: int, 
        document_id: int, 
        uow: UnitOfWork
    ) -> None: 
        session = await uow.session_repo.get_session_chat_by_id(session_id)
        document = await uow.document_repo.get_document_by_id(document_id)
        
        if session is None or session.client_id != client_id: 
            raise SessionIsNotFoundError()
        
        if document is None or document.client_id != client_id: 
            raise DocumentNotFoundError()