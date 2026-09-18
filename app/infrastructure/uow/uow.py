import types
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repositories.client import AbstractClientRepository 
from app.domain.interfaces.repositories.token import AbstractRefreshTokenRepository
from app.infrastructure.database.base import session_factory
from app.infrastructure.repositories.client import ClientRepository 
from app.infrastructure.repositories.token import RefreshTokenRepository


class UnitOfWork: 
    client_repo: AbstractClientRepository
    refresh_token_repo: AbstractRefreshTokenRepository
    
    def __init__(self) -> None: 
        self.session: AsyncSession | None = None
    
    async def __aenter__(self) -> Self: 
        self.session = session_factory()
        self.client_repo = ClientRepository(self.session)
        self.refresh_token_repo = RefreshTokenRepository(self.session)
        return self
    
    async def __aexit__(
        self, 
        exc_type: type[BaseException] | None, 
        exc: BaseException | None, 
        tb: types.TracebackType | None
    ) -> None:
        if exc_type is None: 
            await self.session.commit()
        else: 
            await self.session.rollback()
        await self.session.close()
