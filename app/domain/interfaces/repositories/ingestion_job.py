from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.infrastructure.database.models import IngestionJob
from app.domain.core.enums import IngestionJobStatus, IngestionStage


class AbstractIngestionJobRepository(ABC):
    @abstractmethod 
    async def create_job(
        self, 
        document_id: int, 
        idempotency_key: str, 
        chunking_version: str,
        embedding_model: str,
        embedding_dimension: int, 
        max_attempts: int = 3
    ) -> IngestionJob: ... 
    
    @abstractmethod
    async def get_job(self, job_id: int) -> Optional[IngestionJob]: ...
    
    @abstractmethod
    async def claim_job(
        self, 
        job_id: int, 
        worker_id: str, 
        lease_until: datetime
    ) -> Optional[IngestionJob]: ...
    
    @abstractmethod
    async def update_stage(
        self, 
        job_id: int,
        worker_id: str,
        stage: IngestionStage,
    ) -> Optional[bool]: ...
    
    @abstractmethod
    async def update_status(
        self,
        job_id: int, 
        worker_id: str, 
        status: IngestionJobStatus
    ) -> Optional[bool]: ...
    
    @abstractmethod
    async def set_total_chunks(
        self, 
        job_id: int, 
        worker_id: str, 
        total_chunks: int
    ) -> Optional[bool]: ...
    
    @abstractmethod
    async def update_progress(
        self, 
        job_id: int, 
        worker_id: str,
        processed_chunks: int,
    ) -> Optional[bool]: ...
    
    @abstractmethod
    async def heartbeat(
        self, 
        job_id: int, 
        worker_id: str, 
        heartbeat_at: datetime, 
        lease_until: datetime
    ) -> Optional[bool]: ... 
    
    @abstractmethod
    async def mark_completed(
        self, 
        job_id: int, 
        worker_id: str, 
        finished_at: datetime
    ) -> Optional[bool]: ...
    
    @abstractmethod
    async def mark_failed(
        self, 
        job_id: int, 
        worker_id: str, 
        error_code: str,
        error_message: str,
        finished_at: datetime,
    ) -> Optional[bool]: ...
    
    @abstractmethod
    async def cancel_job(
        self, 
        job_id: int,
        worker_id: str,
        finished_at: datetime
    ) -> Optional[bool]: ...
