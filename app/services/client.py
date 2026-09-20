from sqlalchemy.exc import IntegrityError

from app.domain.core.enums import Role
from app.infrastructure.database.models import Client
from app.infrastructure.uow.uow import UnitOfWork
from app.domain.core.security import security
from app.domain.exceptions.client import ClientAlreadyExistsError


class ClientService: 
    async def register_client(
        self, 
        first_name: str,  
        role: Role, 
        email: str, 
        password: str, 
        last_name: str | None = None
    ) -> Client: 
        # Gen Password Hash
        password_hash = security.hash_password(password)
        
        # Create Client
        async with UnitOfWork() as uow:
            try:
                client = await uow.client_repo.create_client(first_name, role, email, password_hash, last_name)
            except IntegrityError:
                raise ClientAlreadyExistsError()
        
        return client
    