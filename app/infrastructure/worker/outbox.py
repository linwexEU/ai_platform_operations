import asyncio
import logging

from app.infrastructure.uow.uow import UnitOfWork
from app.entrypoints.tasks.chunk import task_create_chunks

logging.basicConfig(level=logging.INFO)


async def main() -> None: 
    while True: 
        async with UnitOfWork() as uow: 
            events = await uow.outbox_repo.get_events()
            
            if not len(events): 
                logging.info("Empty Outbox table. No events.")
            
            for event in events:
                task_create_chunks.delay(event.job_id)
                await uow.outbox_repo.mark_as_published(event.job_id)
                logging.info(f"Queued ingestion job_id={event.job_id}")
                
        await asyncio.sleep(5)
        
        
if __name__ == "__main__": 
    asyncio.run(main())
