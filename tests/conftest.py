import json

import pytest

from app.domain.core.config import settings
from app.infrastructure.uow.uow import UnitOfWork
from app.infrastructure.database.base import engine, Base


@pytest.fixture(scope="session", autouse=True)
def check_test_mode() -> bool: 
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode) -> None: 
    async with engine.begin() as conn: 
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    with open("tests/mocks/mock_clients.json", encoding="utf-8") as file_clients: 
        clients = json.load(file_clients)
        
    with open("tests/mocks/mock_documents.json", encoding="utf-8") as file_documents: 
        documents = json.load(file_documents)
        
    with open("tests/mocks/mock_jobs.json", encoding="utf-8") as file_jobs: 
        jobs = json.load(file_jobs)
        
    async with UnitOfWork() as uow:
        # Add mock clients 
        for client in clients: 
            await uow.client_repo.create_client(
                first_name=client["first_name"], 
                last_name=client["last_name"], 
                role=client["role"], 
                email=client["email"],
                password_hash=client["password_hash"],
                activated=client["activated"]
            )
        
        # Add mock documents
        for document in documents: 
            await uow.document_repo.create_document(
                client_id=int(document["client_id"]), 
                filename=document["filename"],
                mime_type=document["mime_type"], 
                size_bytes=int(document["size_bytes"]),
                storage_key=document["storage_key"]
            )
            
        # Add mock jobs
        for job in jobs: 
            job = await uow.ingestion_job_repo.create_job(
                document_id=int(job["document_id"]),
                idempotency_key=job["idempotency_key"],
                chunking_version=job["chunking_version"],
                embedding_model=settings.OLLAMA_EMBEDDING_MODEL,
                embedding_dimension=settings.EMBEDDING_DIMENSION
            )
            await uow.outbox_repo.create_event(job.id, "CREATE_CHUNKS")
