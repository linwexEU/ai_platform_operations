from typing import Sequence, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.domain.interfaces.repositories.outbox import AbstractOutboxRepository
from app.infrastructure.database.models import Outbox


class OutboxRepository(AbstractOutboxRepository): 
    def __init__(self, session: AsyncSession) -> None: 
        self.session = session
        
    async def create_event(self, job_id: int, event_type: str) -> Outbox:
        event = Outbox(
            job_id=job_id, 
            event_type=event_type
        )
        self.session.add(event) 
        return event
    
    async def get_events(self) -> Sequence[Outbox]:
        events = await self.session.execute(
            select(Outbox)
            .where(Outbox.published.is_(False))
            .order_by(Outbox.id)
            .with_for_update(skip_locked=True)
            .limit(100)
        )
        return events.scalars().all()

    async def mark_as_published(self, job_id: int) -> Optional[bool]:
        stmt = (
            update(Outbox)
            .where(
                Outbox.job_id == job_id, 
                Outbox.published.is_(False)
            )
            .values(published=True)
            .returning(Outbox.id)
        )
        event_id = await self.session.scalar(stmt)
        
        if event_id is None: 
            return False
        return True

    async def delete_published(self) -> None:
        await self.session.execute(
            delete(Outbox)
            .where(
                Outbox.published.is_(True)
            )
        )
