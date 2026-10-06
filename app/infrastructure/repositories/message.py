from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.domain.core.enums import SenderType
from app.domain.interfaces.repositories.message import AbstractMessageRepository
from app.infrastructure.database.models import Message


class MessageRepository(AbstractMessageRepository): 
    def __init__(self, session: AsyncSession) -> None: 
        self.session = session
        
    async def create_message(self, sender: SenderType, session_id: int, text: str) -> Message:
        message = Message(sender=sender, session_id=session_id, text=text)
        self.session.add(message) 
        return message
    
    async def get_messages(self, session_id: int, offset: int = 0, limit: int = 50) -> Sequence[Message]:
        stmt = (
            select(Message)
            .where(
                Message.session_id == session_id
            )
            .offset(offset)
            .limit(limit)
        ) 
        messages = await self.session.execute(stmt) 
        return messages.scalars().all()
    
    async def get_messages_count(self, session_id: int) -> int:
        return await self.session.scalar(
            select(func.count())
            .select_from(Message)
            .where(Message.session_id == session_id)
        ) or 0
    