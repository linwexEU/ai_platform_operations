import asyncio

from app.infrastructure.database.base import engine
from app.infrastructure.worker.celery import app
from app.services.ingestion_job import IngestionJobService


async def _run(job_id: int, worker_id: str) -> None: 
    try: 
        await IngestionJobService().process_job(job_id, worker_id)
    finally: 
        await engine.dispose()


@app.task(bind=True, acks_late=True, max_retries=3)
def task_create_chunks(self, job_id: int) -> None: 
    try:
        asyncio.run(_run(job_id, self.request.id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
