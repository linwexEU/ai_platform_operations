from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, func

from app.domain.interfaces.repositories.session import AbstractSessionRepository
from app.infrastructure.database.models import Session


class SessionRepository(AbstractSessionRepository): 
    def __init__(self, session: AsyncSession) -> None: 
        self.session = session
        
    async def create_session_chat(self, client_id: int, name: str) -> Session:
        session_chat = Session(client_id=client_id, name=name)
        self.session.add(session_chat)
        return session_chat
    
    async def get_client_sessions(self, client_id: int, offset: int = 0, limit: int = 10) -> Sequence[Session]:
        result = await self.session.execute(
            select(Session)
            .where(
                Session.client_id == client_id, 
                Session.deleted_at.is_(None)
            )
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_total_count_clients_sessions(self, client_id: int) -> int: 
        return await self.session.scalar(
            select(
                func.count()
            )
            .select_from(Session)
            .where(
                Session.client_id == client_id, 
                Session.deleted_at.is_(None)
            )
        )
    
    async def get_session_chat_by_id(self, session_id: int) -> Optional[Session]:
        session_chat = await self.session.get(Session, session_id)
        
        if session_chat is None: 
            return None
        
        if session_chat.deleted_at: 
            return None
        
        return session_chat
    
    async def delete_session_chat(self, session_id: int) -> None:
        now = datetime.now(timezone.utc)
        await self.session.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(deleted_at=now)
        )
        
    async def update_session_chat(self, session: Session, name: str) -> None:
        session.name = name
        