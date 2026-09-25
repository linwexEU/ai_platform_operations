import asyncio

from app.infrastructure.worker.celery import app
from app.infrastructure.object_storage.aws_s3 import ObjectStorage

object_storage = ObjectStorage()


async def delete_file_from_s3(key: str) -> None: 
    await object_storage.delete_file(key)


@app.task()
def task_delete_file_from_s3(key: str) -> None: 
    asyncio.run(delete_file_from_s3(key))
