from datetime import datetime
from typing import Sequence

from pydantic import BaseModel

from app.infrastructure.database.models import Session


class CreateSessionRequest(BaseModel): 
    name: str
    
    
class CreateSessionResponse(BaseModel): 
    id: int
    name: str
    created_at: datetime

    @staticmethod
    def from_orm(session: Session) -> "CreateSessionResponse": 
        return CreateSessionResponse(
            id=session.id,
            name=session.name, 
            created_at=session.created_at
        )
        

class UpdateSessionRequest(BaseModel): 
    name: str
    
    
class UpdateSessionResponse(CreateSessionResponse): 
    @staticmethod
    def from_orm(session: Session) -> "UpdateSessionResponse": 
        return UpdateSessionResponse(
            id=session.id,
            name=session.name, 
            created_at=session.created_at
        )
        
        
class SSession(CreateSessionResponse): 
    @staticmethod
    def from_orm(session: Session) -> "SSession": 
        return SSession(
            id=session.id,
            name=session.name, 
            created_at=session.created_at
        ) 


class GetSessionsChatResponse(BaseModel): 
    sessions: list[SSession]
    total_count: int
        