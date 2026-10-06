from abc import ABC, abstractmethod
from typing import Sequence

from app.domain.core.enums import SenderType
from app.infrastructure.database.models import Message


class AbstractMessageRepository(ABC): 
    @abstractmethod
    async def create_message(self, sender: SenderType, session_id: int, text: str) -> Message: ... 
    
    @abstractmethod
    async def get_messages(self, session_id: int, offset: int = 0, limit: int = 50) -> Sequence[Message]: ...
    
    @abstractmethod
    async def get_messages_count(self, session_id: int) -> int: ...
