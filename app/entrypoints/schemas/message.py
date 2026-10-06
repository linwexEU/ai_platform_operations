from typing import Sequence

from pydantic import BaseModel

from app.domain.core.enums import SenderType
from app.infrastructure.database.models import Message


class CreateMessageResponse(BaseModel): 
    text: str
    sender: SenderType


class SMessage(BaseModel): 
    id: int
    session_id: int
    sender: SenderType
    text: str
    
    @staticmethod
    def from_orm(message: Message) -> "SMessage": 
        return SMessage(
            id=message.id,
            session_id=message.session_id,
            sender=message.sender,
            text=message.text
        )


class GetMessagesResponse(BaseModel): 
    messages: list[SMessage]
    total: int
    
    @staticmethod
    def from_orm(messages: Sequence[Message], total: int) -> "GetMessagesResponse": 
        return GetMessagesResponse(
            messages=[SMessage.from_orm(message) for message in messages], 
            total=total
        )
     