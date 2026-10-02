from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.domain.interfaces.repositories.client import AbstractClientRepository
from app.infrastructure.database.models import Client
from app.domain.core.enums import Role


class ClientRepository(AbstractClientRepository): 
    def __init__(self, session: AsyncSession) -> None: 
        self.session = session
        
    async def create_client(
        self, 
        first_name: str, 
        role: Role, 
        email: str, 
        password_hash: str, 
        last_name: str | None = None, 
        activated: bool = False
    ) -> Client:
        client = Client(
            first_name=first_name, 
            last_name=last_name,
            role=role,
            email=email,
            password_hash=password_hash,
            activated=activated
        )
        self.session.add(client)
        return client
    
    async def get_client_by_id(self, client_id: int) -> Optional[Client]: 
        return await self.session.get(Client, client_id)
    
    async def get_client_by_email(self, email: str) -> Optional[Client]: 
        return await self.session.scalar(select(Client).where(Client.email == email))
    
    async def verify_client(self, client_id: int) -> None: 
        await self.session.execute(
            update(Client).where(Client.id == client_id).values(activated=True)
        )
