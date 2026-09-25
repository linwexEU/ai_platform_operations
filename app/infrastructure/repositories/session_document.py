from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.domain.interfaces.repositories.session_document import AbstractSessionDocumentRepository
from app.infrastructure.database.models import SessionDocument


class SessionDocumentRepository(AbstractSessionDocumentRepository): 
    def __init__(self, session: AsyncSession): 
        self.session = session
        
    async def attach_document_to_session(self, session_id: int, document_id: int) -> None:
        attachment = SessionDocument(
            session_id=session_id, 
            document_id=document_id
        ) 
        self.session.add(attachment)
        
    async def detach_document_from_session(self, session_id: int, document_id: int) -> None:
        await self.session.execute(
            delete(SessionDocument)
            .where(
                SessionDocument.session_id == session_id, 
                SessionDocument.document_id == document_id
            )
        )
    