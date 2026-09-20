from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from app.infrastructure.database.models import VerificationCode


class AbstractVerificationCodeRepository(ABC): 
    @abstractmethod
    async def create_verification_code(self, client_id: int, code: str, expires_at: datetime) -> VerificationCode: ...
    
    @abstractmethod
    async def get_verification_code(self, code: str) -> Optional[VerificationCode]: ...

    @abstractmethod
    async def delete_verification_codes(self, client_id: int) -> None: ...