from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.domain.interfaces.repositories.token import AbstractRefreshTokenRepository
from app.infrastructure.database.models import RefreshToken


class RefreshTokenRepository(AbstractRefreshTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def create_refresh_token(self, client_id: int, token_hash: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(
            client_id=client_id, 
            token_hash=token_hash, 
            expires_at=expires_at
        )
        self.session.add(token)
        await self.session.flush()
        return token
    
    async def get_refresh_token_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        return await self.session.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    
    async def revoke_refresh_token_by_hash(self, token_hash: str) -> Optional[int]:
        return await self.session.scalar(
            update(RefreshToken).where(RefreshToken.token_hash == token_hash).values(revoked=True).returning(RefreshToken.id)
        )
