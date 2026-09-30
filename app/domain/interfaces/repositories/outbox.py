from abc import ABC, abstractmethod
from typing import Sequence, Optional

from app.infrastructure.database.models import Outbox


class AbstractOutboxRepository(ABC): 
    @abstractmethod
    async def create_event(self, job_id: int, event_type: str) -> Outbox: ... 

    @abstractmethod
    async def get_events(self) -> Sequence[Outbox]: ...

    @abstractmethod
    async def mark_as_published(self, job_id: int) -> Optional[bool]: ...

    @abstractmethod
    async def delete_published(self) -> None: ...
