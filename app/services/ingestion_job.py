import asyncio
from datetime import datetime, timezone, timedelta
import math
import os
import pathlib

import aiofiles
import aiohttp

from app.domain.core.enums import IngestionJobStatus, IngestionStage
from app.domain.core.config import settings
from app.infrastructure.object_storage.aws_s3 import ObjectStorage
from app.infrastructure.uow.uow import UnitOfWork
from app.infrastructure.reader.pdf_reader import PDFReader
from app.infrastructure.embeddings.ollama import generate_embedding
from app.infrastructure.chunking.splitter import document_splitter
from app.domain.exceptions.embedding import (
    EmbeddingDimensionError,
    EmbeddingValueError
)


class IngestionJobService: 
    def __init__(self) -> None:
        self.object_storage = ObjectStorage()
        self.session: aiohttp.ClientSession | None = None
        self.filename: str | None = None
    
    async def process_job(self, job_id: int, worker_id: str) -> None:
        # Ensure http session
        await self._ensure_session()
        try:
            # Define lease until 
            started_at = datetime.now(timezone.utc)
            lease_until = started_at + timedelta(minutes=15)
            
            # Claim job
            async with UnitOfWork() as uow: 
                job = await uow.ingestion_job_repo.claim_job(job_id, worker_id, started_at, lease_until)
                
                if job is None: 
                    return
                
                if job.status == IngestionJobStatus.Completed:  # Idempotent
                    return
                
                # Get document
                document = await uow.document_repo.get_document_by_id(job.document_id)
                
                if document is None: 
                    await uow.ingestion_job_repo.mark_failed(
                        job_id, 
                        worker_id,
                        error_message=f"Document(Id={job.document_id}) not found",
                        finished_at=datetime.now(timezone.utc)
                    )
                    return
                
            try:
                # Download document
                await self._update_stage(job_id, worker_id, IngestionStage.Downloading)
                await self._download(document.storage_key)
                
                # Chunking
                await self._update_stage(job_id, worker_id, IngestionStage.Chunking)
                chunks = await asyncio.to_thread(self._split)
                
                # Embedding
                await self._update_stage(job_id, worker_id, IngestionStage.Embedding)
                await self._embed_and_save(job_id, worker_id, job.document_id, chunks, settings.EMBEDDING_DIMENSION)
                
                # Mark completed
                async with UnitOfWork() as uow:
                    await uow.ingestion_job_repo.set_total_chunks(job_id, worker_id, len(chunks))
                    await uow.ingestion_job_repo.mark_completed(job_id, worker_id, datetime.now(timezone.utc))
            except Exception as err:
                async with UnitOfWork() as uow: 
                    await uow.ingestion_job_repo.mark_failed(
                        job_id, 
                        worker_id,
                        "500", 
                        str(err.args[0])[:64], 
                        datetime.now(timezone.utc)
                    )
                raise
        finally:         
            # Clear and release resources
            await asyncio.to_thread(self._clear_temp_folder)
            await self.session.close()
            self.session = None
        
    async def _download(self, storage_key: str) -> None: 
        # Download document from S3 to local temp folder
        document_bytes = await self.object_storage.read_file(storage_key)
        
        # Specify a filename
        self.filename = storage_key.replace("/", "_")
        
        # Load
        async with aiofiles.open(pathlib.Path(f"{settings.TEMP_FOLDER_PATH}") / pathlib.Path(self.filename), "wb") as file: 
            await file.write(document_bytes) 
        
    def _split(self) -> list[str]: 
        # Get text from PDF file
        reader = PDFReader(pathlib.Path(f"{settings.TEMP_FOLDER_PATH}") / pathlib.Path(self.filename)) 
        cleaned_text = reader.get_cleaned_text()
        
        # Split
        return document_splitter(cleaned_text)
    
    async def _embed_and_save(
        self,
        job_id: int,
        worker_id: str,
        document_id: int,
        chunks: list[str],
        expected_dim: int
    ) -> None: 
        sem = asyncio.Semaphore(settings.MAX_CONCURRENT) 
        
        async def embed_one(text: str) -> list[float]: 
            async with sem: 
                return await generate_embedding(self.session, text)
            
        for start in range(0, len(chunks), settings.EMBEDDING_BATCH): 
            batch = chunks[start:start + settings.EMBEDDING_BATCH]
            
            # Bounded embed 
            embedding = await asyncio.gather(
                *(embed_one(t) for t in batch)
            )
            
            # Validate before touiching the DB - one bad vector will poison the batch
            for emb in embedding: 
                if len(emb) != expected_dim: 
                    raise EmbeddingDimensionError(f"got {len(emb)}, want {expected_dim}")
                if not all(math.isfinite(x) for x in emb): 
                    raise EmbeddingValueError("non-finite value in embedding")
                
            # One short tx: chunks + progress
            async with UnitOfWork() as uow: 
                for offset, (text, emb) in enumerate(zip(batch, embedding)): 
                    await uow.chunk_repo.create_chunk(
                        document_id, start + offset, text, emb
                    )
                await uow.ingestion_job_repo.update_progress(job_id, worker_id, start + len(batch))
    
    async def _ensure_session(self) -> None: 
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
            
    async def _update_stage(self, job_id: int, worker_id: str, stage: IngestionStage) -> None:
        heartbeated_at = datetime.now(timezone.utc)
        async with UnitOfWork() as uow:
            await uow.ingestion_job_repo.update_stage(job_id, worker_id, stage)
            await uow.ingestion_job_repo.heartbeat(job_id, worker_id, heartbeated_at, heartbeated_at + timedelta(minutes=15))
        
    def _clear_temp_folder(self) -> None: 
        if self.filename:
            os.remove(pathlib.Path(settings.TEMP_FOLDER_PATH) / pathlib.Path(self.filename))
    