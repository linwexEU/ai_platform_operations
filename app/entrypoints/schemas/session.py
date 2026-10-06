from datetime import datetime

from pydantic import BaseModel

from app.entrypoints.schemas.document import SDocument
from app.entrypoints.schemas.message import SMessage
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
        
        
class SSessionFull(CreateSessionResponse): 
    documents: list[SDocument]
    messages: list[SMessage]
    
    @staticmethod
    def from_orm(session: Session) -> "SSessionFull":
        # Fill documents
        documents = []
        for session_document in session.session_document: 
            documents.append(
                SDocument.from_orm(session_document.document)
            )
        
        # Fill messages
        messages = []
        for message in session.messages: 
            messages.append(
                SMessage.from_orm(message)
            )   
              
        return SSessionFull(
            id=session.id,
            name=session.name, 
            created_at=session.created_at, 
            documents=documents, 
            messages=messages
        )


class GetSessionsChatResponse(BaseModel): 
    sessions: list[SSession]
    total_count: int
