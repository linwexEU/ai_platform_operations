import asyncio
from typing import Sequence, Optional

from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.domain.core.enums import SenderType
from app.domain.exceptions.document import DocumentNotFoundError
from app.domain.exceptions.session import SessionIsNotFoundError
from app.domain.exceptions.session_document import DocumentAlreadyAttachedError
from app.infrastructure.database.models import Message, Session
from app.infrastructure.repositories.session import SessionRepository
from app.infrastructure.uow.uow import UnitOfWork
from app.infrastructure.embeddings.ollama import generate_embedding


class SessionService: 
    def __init__(self, session: AsyncSession, http_client: ClientSession) -> None:
        self.repo = SessionRepository(session)
        self.http_client = http_client
        
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
        
        if session_chat is None or session_chat.client_id != client_id: 
            raise SessionIsNotFoundError()
        
        return session_chat
    
    async def update_session_chat(self, client_id: int, session_id: int, name: str) -> Session: 
        async with UnitOfWork() as uow: 
            session_chat = await self._validate_session(client_id, session_id, uow)
            await uow.session_repo.update_session_chat(session_chat, name)
        
        return session_chat
    
    async def delete_session_chat(self, client_id: int, session_id: int) -> None: 
        async with UnitOfWork() as uow: 
            await self._validate_session(client_id, session_id, uow)
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

    async def save_message(
        self, 
        client_id: int, 
        session_id: int,
        sender: SenderType, 
        text: str
    ) -> None: 
        async with UnitOfWork() as uow: 
            await self._validate_session(client_id, session_id, uow)            
            await uow.message_repo.create_message(sender, session_id, text)
    
    async def get_messages(
        self, 
        client_id: int, 
        session_id: int, 
        offset: int, 
        limit: int
    ) -> tuple[Sequence[Message], int]: 
        async with UnitOfWork() as uow: 
            await self._validate_session(client_id, session_id, uow)  
            messages, total = await asyncio.gather(
                uow.message_repo.get_messages(session_id, offset, limit),
                uow.message_repo.get_messages_count(session_id)
            )
            return messages, total
    
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
            
    async def _validate_session(self, client_id: int, session_id: int, uow: UnitOfWork) -> Session: 
        session = await uow.session_repo.get_session_chat_by_id(session_id)
        if session is None or session.client_id != client_id: 
            raise SessionIsNotFoundError()
        return session
    
    async def _find_similar_chunks(
        self,
        session_id: int, 
        input_: str
    ) -> list[str]: 
        # Generate embedding for input
        embedding_input = await generate_embedding(self.http_client, input_)
        
        # Retrieve similar
        async with UnitOfWork() as uow: 
            chunks = await uow.chunk_repo.retrieve_similar(session_id, embedding_input)
        return [chunk.text for chunk in chunks]
