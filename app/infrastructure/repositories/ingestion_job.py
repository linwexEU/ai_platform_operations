from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_, and_

from app.domain.interfaces.repositories.ingestion_job import AbstractIngestionJobRepository
from app.infrastructure.database.models import IngestionJob
from app.domain.core.enums import IngestionJobStatus, IngestionStage


class IngestionJobRepository(AbstractIngestionJobRepository): 
    def __init__(self, session: AsyncSession) -> None: 
        self.session = session
        
    async def create_job(
        self, 
        document_id, 
        idempotency_key, 
        chunking_version, 
        embedding_model, 
        embedding_dimension, 
        max_attempts = 3
    ) -> IngestionJob:
        job = IngestionJob(
            document_id=document_id, 
            idempotency_key=idempotency_key, 
            chunking_version=chunking_version,
            embedding_model=embedding_model,
            embedding_dimension=embedding_dimension,
            max_attempts=max_attempts
        )
        self.session.add(job) 
        await self.session.flush()
        return job
    
    async def get_job(self, job_id: int) -> Optional[IngestionJob]:
        return await self.session.get(IngestionJob, job_id)

    async def claim_job(
        self, 
        job_id: int, 
        worker_id: str, 
        lease_until: datetime
    ) -> Optional[IngestionJob]:
        now = datetime.now(timezone.utc)
        stmt = (
            update(IngestionJob)
            .where(
                IngestionJob.id == job_id,
                or_(
                    IngestionJob.status == IngestionJobStatus.Queued, 
                    and_(
                        IngestionJob.status == IngestionJobStatus.Processing, 
                        IngestionJob.lease_until < now
                    )
                ),
                IngestionJob.attempt_count < IngestionJob.max_attempts
            )
            .values(
                status=IngestionJobStatus.Processing,
                worker_id=worker_id, 
                lease_until=lease_until,
                attempt_count=IngestionJob.attempt_count + 1
            )
            .returning(IngestionJob)
        )
        
        job = await self.session.execute(stmt)
        return job.scalar_one_or_none()

    async def update_stage(
        self, 
        job_id: int, 
        worker_id: str, 
        stage: IngestionStage
    ) -> Optional[bool]:
        job = await self._get_job(job_id, worker_id)
        
        if job is not None: 
            job.stage = stage
        else: 
            return False

    async def update_status(
        self, 
        job_id: int, 
        worker_id: str, 
        status: IngestionJobStatus
    ) -> Optional[bool]:
        job = await self._get_job(job_id, worker_id)
        
        if job is not None: 
            job.status = status
        else: 
            return False

    async def set_total_chunks(
        self, 
        job_id: int, 
        worker_id: str, 
        total_chunks: int
    ) -> Optional[bool]:
        job = await self._get_job(job_id, worker_id)
        
        if job is not None: 
            job.total_chunks = total_chunks
        else: 
            return False
            
    async def update_progress(
        self, 
        job_id: int, 
        worker_id: str, 
        processed_chunks: int
    ) -> Optional[bool]:
        job = await self._get_job(job_id, worker_id)
        
        if job is not None: 
            job.processed_chunks = processed_chunks
        else: 
            return False

    async def heartbeat(
        self, 
        job_id: int, 
        worker_id: str, 
        heartbeat_at: datetime, 
        lease_until: datetime
    ) -> Optional[bool]:
        job = await self._get_job(job_id, worker_id)
        
        if job is not None: 
            job.last_heartbeat_at = heartbeat_at
            job.lease_until = lease_until
        else: 
            return False
            
    async def mark_completed(
        self, 
        job_id: int, 
        worker_id: str, 
        finished_at: datetime
    ) -> Optional[bool]:
        job = await self._get_job(job_id, worker_id)
        
        if job is not None: 
            job.status = IngestionJobStatus.Completed
            job.stage =IngestionStage.Finalizing
            job.finished_at = finished_at
        else: 
            return False
            
    async def mark_failed(
        self, 
        job_id: int, 
        worker_id: str,
        error_code: str, 
        error_message: str, 
        finished_at: datetime
    ) -> Optional[bool]:
        job = await self._get_job(job_id, worker_id)
        
        if job is not None: 
            job.status = IngestionJobStatus.Failed
            job.last_error_code = error_code
            job.last_error_message = error_message
            job.finished_at = finished_at
        else: 
            return False
            
    async def cancel_job(
        self, 
        job_id: int, 
        worker_id: str, 
        finished_at: datetime
    ) -> Optional[bool]:
        job = await self._get_job(job_id, worker_id)
                
        if job is not None: 
            job.status = IngestionJobStatus.Cancelled
            job.finished_at = finished_at
        else: 
            return False
        
    async def _get_job(self, job_id: int, worker_id: str) -> Optional[IngestionJob]: 
        return await self.session.scalar(
            select(IngestionJob)
            .where(
                IngestionJob.id == job_id, 
                IngestionJob.worker_id == worker_id
            )
        )
        