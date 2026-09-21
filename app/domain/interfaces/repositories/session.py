from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.infrastructure.database.models import Session


class AbstractSessionRepository(ABC): 
    @abstractmethod
    async def create_session_chat(self, client_id: int, name: str) -> Session: ...
    
    @abstractmethod
    async def get_client_sessions(self, client_id: int) -> Sequence[Session]: ...
    
    @abstractmethod
    async def get_session_chat_by_id(self, session_id: int) -> Optional[Session]: ... 
        
    @abstractmethod
    async def delete_session_chat(self, session_id: int) -> None: ...
    
    @abstractmethod
    async def update_session_chat(self, session_id: int, name: str) -> Optional[Session]: ...
