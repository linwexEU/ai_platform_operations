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
        document_id: int, 
        idempotency_key: str, 
        chunking_version: str, 
        embedding_model: str, 
        embedding_dimension: int, 
        max_attempts: int = 3
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
        started_at: datetime,
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
                attempt_count=IngestionJob.attempt_count + 1,
                started_at=started_at
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
    ) -> bool:
        stmt = (
            update(IngestionJob)
            .where(
                IngestionJob.id == job_id,
                IngestionJob.worker_id == worker_id
            )
            .values(
                stage=stage
            )
            .returning(
                IngestionJob.id
            )
        )
        job = await self.session.execute(stmt)
        
        if not job.scalar_one_or_none(): 
            return False
        return True

    async def set_total_chunks(
        self, 
        job_id: int, 
        worker_id: str, 
        total_chunks: int
    ) -> bool:
        stmt = (
            update(IngestionJob)
            .where(
                IngestionJob.id == job_id,
                IngestionJob.worker_id == worker_id
            )
            .values(
                total_chunks=total_chunks
            )
            .returning(
                IngestionJob.id
            )
        )
        job = await self.session.execute(stmt)
        
        if not job.scalar_one_or_none(): 
            return False
        return True
            
    async def update_progress(
        self, 
        job_id: int, 
        worker_id: str, 
        processed_chunks: int
    ) -> bool:
        stmt = (
            update(IngestionJob)
            .where(
                IngestionJob.id == job_id,
                IngestionJob.worker_id == worker_id
            )
            .values(
                processed_chunks=processed_chunks
            )
            .returning(IngestionJob.id)
        )
        
        job = await self.session.execute(stmt)
        
        if not job.scalar_one_or_none(): 
            return False
        return True

    async def heartbeat(
        self, 
        job_id: int, 
        worker_id: str, 
        heartbeat_at: datetime, 
        lease_until: datetime
    ) -> bool:
        stmt = (
            update(IngestionJob)
            .where(
                IngestionJob.id == job_id,
                IngestionJob.worker_id == worker_id
            )
            .values(
                last_heartbeat_at=heartbeat_at,
                lease_until=lease_until
            )
            .returning(IngestionJob.id)
        )
        
        job = await self.session.execute(stmt)
        
        if not job.scalar_one_or_none(): 
            return False
        return True
            
    async def mark_completed(
        self, 
        job_id: int, 
        worker_id: str, 
        finished_at: datetime
    ) -> bool:
        stmt = (
            update(IngestionJob)
            .where(
                IngestionJob.id == job_id,
                IngestionJob.worker_id == worker_id
            )
            .values(
                status=IngestionJobStatus.Completed,
                stage=IngestionStage.Completed,
                finished_at=finished_at
            )
            .returning(IngestionJob.id)
        )
        job = await self.session.execute(stmt)
                
        if not job.scalar_one_or_none(): 
            return False
        return True
            
    async def mark_failed(
        self, 
        job_id: int, 
        worker_id: str,
        error_code: str, 
        error_message: str, 
        finished_at: datetime
    ) -> bool:
        stmt = (
            update(IngestionJob)
            .where(
                IngestionJob.id == job_id,
                IngestionJob.worker_id == worker_id
            )
            .values(
                status=IngestionJobStatus.Failed,
                last_error_code=error_code,
                last_error_message=error_message,
                finished_at=finished_at
            )
            .returning(IngestionJob.id)
        )
        job = await self.session.execute(stmt)
                        
        if not job.scalar_one_or_none(): 
            return False
        return True
