import types
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repositories.chunk import AbstractChunkRepository
from app.domain.interfaces.repositories.client import AbstractClientRepository 
from app.domain.interfaces.repositories.document import AbstractDocumentRepository
from app.domain.interfaces.repositories.ingestion_job import AbstractIngestionJobRepository
from app.domain.interfaces.repositories.message import AbstractMessageRepository
from app.domain.interfaces.repositories.outbox import AbstractOutboxRepository
from app.domain.interfaces.repositories.session import AbstractSessionRepository
from app.domain.interfaces.repositories.session_document import AbstractSessionDocumentRepository
from app.domain.interfaces.repositories.token import AbstractRefreshTokenRepository
from app.domain.interfaces.repositories.verification_code import AbstractVerificationCodeRepository
from app.infrastructure.database.base import session_factory
from app.infrastructure.repositories.chunk import ChunkRepository
from app.infrastructure.repositories.client import ClientRepository 
from app.infrastructure.repositories.document import DocumentRepository
from app.infrastructure.repositories.ingestion_job import IngestionJobRepository
from app.infrastructure.repositories.message import MessageRepository
from app.infrastructure.repositories.outbox import OutboxRepository
from app.infrastructure.repositories.session import SessionRepository
from app.infrastructure.repositories.session_document import SessionDocumentRepository
from app.infrastructure.repositories.token import RefreshTokenRepository
from app.infrastructure.repositories.verification_code import VerificationCodeRepository


class UnitOfWork: 
    client_repo: AbstractClientRepository
    refresh_token_repo: AbstractRefreshTokenRepository
    verification_code_repo: AbstractVerificationCodeRepository
    session_repo: AbstractSessionRepository
    document_repo: AbstractDocumentRepository
    session_document_repo: AbstractSessionDocumentRepository
    chunk_repo: AbstractChunkRepository
    ingestion_job_repo: AbstractIngestionJobRepository
    outbox_repo: AbstractOutboxRepository
    message_repo: AbstractMessageRepository
    
    def __init__(self) -> None: 
        self.session: AsyncSession | None = None
    
    async def __aenter__(self) -> Self: 
        self.session = session_factory()
        self.client_repo = ClientRepository(self.session)
        self.refresh_token_repo = RefreshTokenRepository(self.session)
        self.verification_code_repo = VerificationCodeRepository(self.session)
        self.session_repo = SessionRepository(self.session)
        self.document_repo = DocumentRepository(self.session)
        self.session_document_repo = SessionDocumentRepository(self.session)
        self.chunk_repo = ChunkRepository(self.session)
        self.ingestion_job_repo = IngestionJobRepository(self.session)
        self.outbox_repo = OutboxRepository(self.session)
        self.message_repo = MessageRepository(self.session)
        return self
    
    async def __aexit__(
        self, 
        exc_type: type[BaseException] | None, 
        exc: BaseException | None, 
        tb: types.TracebackType | None
    ) -> None:
        if exc_type is None: 
            await self.session.commit()
        else: 
            await self.session.rollback()
        await self.session.close()
