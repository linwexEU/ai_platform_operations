from abc import ABC, abstractmethod
from typing import Optional

from app.domain.core.enums import Role
from app.infrastructure.database.models import Client


class AbstractClientRepository(ABC): 
    @abstractmethod
    async def create_client(
        self, 
        first_name: str,
        role: Role,
        email: str,
        password_hash: str, 
        last_name: str | None = None,
        activated: bool = False
    ) -> Client: ...

    @abstractmethod
    async def get_client_by_id(self, client_id: int) -> Optional[Client]: ...

    @abstractmethod
    async def get_client_by_email(self, email: str) -> Optional[Client]: ...

    @abstractmethod
    async def verify_client(self, client_id: int) -> None: ...
