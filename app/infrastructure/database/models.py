from datetime import datetime
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, 
    Enum, 
    DateTime, 
    ForeignKey, 
    Boolean, 
    Integer, 
    JSON, 
    Text, 
    func, 
    UniqueConstraint, 
    SMALLINT
)
from pgvector.sqlalchemy import Vector

from app.infrastructure.database.base import Base
from app.domain.core.enums import (
    DocumentStatus, 
    Role, 
    SenderType, 
    OperationType, 
    OperationStatus, 
    IngestionJobStatus, 
    IngestionStage
)


class Client(Base): 
    __tablename__ = "client"
    
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=True)
    role: Mapped[Role] = mapped_column(Enum(Role, name="client_role"), nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    activated: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    verification_codes: Mapped[list["VerificationCode"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    sessions: Mapped[list["Session"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    
    
class RefreshToken(Base): 
    __tablename__ = "refresh_token"
    
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column (Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client: Mapped["Client"] = relationship(back_populates="refresh_tokens")


class VerificationCode(Base): 
    __tablename__ = "verification_code"
    
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(128), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    client: Mapped["Client"] = relationship(back_populates="verification_codes")


class Session(Base): 
    __tablename__ = "session"
    
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    client: Mapped["Client"] = relationship(back_populates="sessions")
    session_document: Mapped[list["SessionDocument"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    messages: Mapped[list["Message"]] = relationship(back_populates="session")
    operations: Mapped[list["Operation"]] = relationship(back_populates="session")
    
    
class Document(Base): 
    __tablename__ = "document"
    
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(128), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus, name="document_status"), default=DocumentStatus.Uploading)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    client: Mapped["Client"] = relationship(back_populates="documents")
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    session_document: Mapped[list["SessionDocument"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    ingestion_jobs: Mapped[list["IngestionJob"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(Base): 
    __tablename__ = "chunk"
    
    document_id: Mapped[int] = mapped_column(ForeignKey("document.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(768), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    document: Mapped["Document"] = relationship(back_populates="chunks")
    
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),
    )
    

class IngestionJob(Base): 
    __tablename__ = "ingestion_job"
    
    document_id: Mapped[int] = mapped_column(ForeignKey("document.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[IngestionJobStatus] = mapped_column(
        Enum(IngestionJobStatus, name="ingestion_job_status"), 
        default=IngestionJobStatus.Queued, 
        index=True, 
        nullable=False
    )
    stage: Mapped[IngestionStage] = mapped_column(
        Enum(IngestionStage, name="ingestion_stage"), 
        default=IngestionStage.Pending, 
        nullable=False
    )
    attempt_count: Mapped[int] = mapped_column(SMALLINT, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(SMALLINT, default=3, nullable=False)
    total_chunks: Mapped[int] = mapped_column(Integer, nullable=True)
    processed_chunks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    worker_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    chunking_version: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("document_id", "idempotency_key", name="uq_doc_idempotency_key"),
    )
    
    document: Mapped["Document"] = relationship(back_populates="ingestion_jobs")


class SessionDocument(Base): 
    __tablename__ = "session_document"
    
    document_id: Mapped[int] = mapped_column(ForeignKey("document.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[int] = mapped_column(ForeignKey("session.id", ondelete="CASCADE"), nullable=False)
    
    session: Mapped["Session"] = relationship(back_populates="session_document")
    document: Mapped["Document"] = relationship(back_populates="session_document")
    
    __table_args__ = (
        UniqueConstraint("document_id", "session_id", name="uq_document_id_session_id"),
    )
    
    
class Message(Base): 
    __tablename__ = "message"
    
    sender: Mapped[SenderType] = mapped_column(Enum(SenderType, name="sender_type"), nullable=False)
    session_id: Mapped[int] = mapped_column(ForeignKey("session.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    session: Mapped["Session"] = relationship(back_populates="messages")
    
    
class Operation(Base): 
    __tablename__ = "operation"
    
    type: Mapped[OperationType] = mapped_column(Enum(OperationType, name="operation_type"), nullable=False)
    session_id: Mapped[int] = mapped_column(ForeignKey("session.id", ondelete="CASCADE"), nullable=False)
    params: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus, name="operation_status"), default=OperationStatus.Pending)
    result_ref: Mapped[str] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    session: Mapped["Session"] = relationship(back_populates="operations")


class Outbox(Base): 
    __tablename__ = "outbox"
    
    job_id: Mapped[int] = mapped_column(ForeignKey("ingestion_job.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, index=True, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    