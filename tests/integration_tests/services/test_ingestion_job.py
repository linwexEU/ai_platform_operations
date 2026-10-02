from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, AsyncMock

from app.domain.core.enums import IngestionJobStatus, IngestionStage
from app.services.ingestion_job import IngestionJobService
from app.infrastructure.reader.pdf_reader import PDFReader
from app.infrastructure.chunking.splitter import document_splitter
from app.infrastructure.uow.uow import UnitOfWork


class TestIngestionJobService: 
    async def test_process_job(self) -> None: 
        # Init service
        service, chunks = self._get_mocked_service()
        
        # Process the job
        await service.process_job(1, "test-worker-1")
        
        # Validate
        async with UnitOfWork() as uow: 
            job = await uow.ingestion_job_repo.get_job(1)
            
            assert job.status == IngestionJobStatus.Completed
            assert job.stage == IngestionStage.Finalizing
            assert job.total_chunks == len(chunks)
            assert job.processed_chunks == len(chunks)
            
    def _get_mock_pdf_splitted(self) -> list[str]: 
        reader = PDFReader("tests/mocks/mock_resume.pdf")
        cleaned_text = reader.get_cleaned_text()
        return document_splitter(cleaned_text)

    def _get_mocked_service(self) -> tuple[IngestionJobService, list[str]]: 
        # Init service
        service = IngestionJobService()
        
        # Mock _download method
        service._download = AsyncMock(return_value=None)
        
        # Mock _split method
        chunks = self._get_mock_pdf_splitted()
        service._split = MagicMock(return_value=chunks)
        
        # Mock _clear_temp_folder
        service._clear_temp_folder = MagicMock(return_value=None)
        
        return service, chunks
