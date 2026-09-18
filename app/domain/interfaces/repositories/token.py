from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.infrastructure.database.models import RefreshToken


class AbstractRefreshTokenRepository(ABC):
    @abstractmethod
    async def create_refresh_token(
        self, 
        client_id: int,
        token_hash: str,
        expires_at: datetime
    ) -> RefreshToken: ... 
    
    @abstractmethod
    async def get_refresh_token_by_hash(self, token_hash: str) -> Optional[RefreshToken]: ...

    @abstractmethod 
    async def revoke_refresh_token_by_hash(self, token_hash: str) -> Optional[int]: ...
