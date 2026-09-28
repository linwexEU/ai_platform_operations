import asyncio
import os
import pathlib

from app.infrastructure.embeddings.ollama import generate_embeddings
from app.infrastructure.reader.pdf_reader import PDFReader
from app.infrastructure.uow.uow import UnitOfWork
from app.infrastructure.http_clients.aiohttp_client import HttpClient
from app.infrastructure.chunking.splitter import document_splitter
from app.domain.core.config import settings
from app.infrastructure.worker.celery import app


async def create_chunks(doc_id: int, doc_url: str, storage_key: str) -> None:
    storage_key = storage_key.replace("/", "_")
    
    # Init HttpClient
    client = HttpClient()
    
    # Download doc to memory
    await client.download(doc_url, storage_key)
    
    # Init reader
    reader = PDFReader(pathlib.Path(settings.TEMP_FOLDER_PATH) / pathlib.Path(storage_key)) 
    document_text = await asyncio.to_thread(reader.get_cleaned_text)
    
    # Spit document text
    chunks = document_splitter(document_text)

    # Get embeddings
    embeddings = await generate_embeddings(client.session, chunks)
    
    # Save chunks
    async with UnitOfWork() as uow: 
        for chunk_index, chunk in enumerate(chunks):
            await uow.chunk_repo.create_chunk(
                doc_id, chunk_index, chunk, embeddings[chunk_index]
            )
    
    # Close session  
    await client.close_session()
    
    # Clear temp folder
    os.remove(pathlib.Path(settings.TEMP_FOLDER_PATH) / pathlib.Path(storage_key))


@app.task()
def task_create_chunks(doc_id: int, doc_url: str, storage_key: str) -> None: 
    asyncio.run(create_chunks(doc_id, doc_url, storage_key))
