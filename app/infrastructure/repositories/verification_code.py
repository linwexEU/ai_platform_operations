from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete

from app.domain.interfaces.repositories.verification_code import AbstractVerificationCodeRepository
from app.infrastructure.database.models import VerificationCode


class VerificationCodeRepository(AbstractVerificationCodeRepository): 
    def __init__(self, session: AsyncSession) -> None: 
        self.session = session
        
    async def create_verification_code(self, client_id: int, code: str, expires_at: datetime) -> VerificationCode: 
        verification_code = VerificationCode(client_id=client_id, code=code, expires_at=expires_at)
        self.session.add(verification_code)
        await self.session.flush()
        return verification_code
    
    async def get_verification_code(self, code: str) -> Optional[VerificationCode]:
        return await self.session.scalar(
            select(VerificationCode).where(VerificationCode.code == code).options(
                selectinload(VerificationCode.client)
            )
        )
    
    async def delete_verification_codes(self, client_id: int) -> None:
        await self.session.execute(
            delete(VerificationCode).where(VerificationCode.client_id == client_id)
        )
