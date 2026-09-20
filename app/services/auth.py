import asyncio
from datetime import datetime, timezone, timedelta
import logging
import uuid

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.core.tokens import tokens
from app.domain.core.security import security
from app.domain.core.config import settings
from app.entrypoints.tasks.auth import task_send_verification_code
from app.infrastructure.uow.uow import UnitOfWork
from app.infrastructure.database.models import Client, RefreshToken
from app.infrastructure.repositories.client import ClientRepository
from app.domain.exceptions.tokens import InvalidCredentialsError
from app.domain.exceptions.client import ClientNotFoundError
from app.domain.exceptions.tokens import (
    RefreshTokenExpiredError, 
    RefreshTokenNotFoundError
)
from app.domain.exceptions.verification_code import (
    VerificationCodeNotFoundError,
    VerificationCodeExpiredError
)

logger = logging.getLogger(__name__)


class AuthService: 
    def __init__(self, session: AsyncSession) -> None: 
        self.session = session
        
    async def login(self, email: str, password: str) -> tuple[str, str]: 
        client = await self._get_client_or_raise(email, password)
        pair = await self._issue_token(client.id)
        
        # Create verification code
        if not client.activated:
            code = str(uuid.uuid4()).split("-")[-1]
            async with UnitOfWork() as uow: 
                await uow.verification_code_repo.create_verification_code(
                    client_id=client.id, 
                    code=code, 
                    expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.VERIFICATION_CODE_MINUTES)
                )
                    
            # Send email with verification code
            task_send_verification_code.delay(code, email)
            
        return pair
    
    async def verify_account(self, code: str, email: EmailStr) -> None: 
        async with UnitOfWork() as uow: 
            verification_code = await uow.verification_code_repo.get_verification_code(code)
            
            if verification_code is None: 
                logger.error(f"Verification code = {code} is not found")
                raise VerificationCodeNotFoundError()
            
            if verification_code.client.email != email: 
                logger.error(f"Verification.client.email(verification_code.client.email)  != email({email})")
                raise InvalidCredentialsError()
            
            if datetime.now(timezone.utc) >= verification_code.expires_at: 
                logger.error(f"Verification code {verification_code.code} has expired")
                raise VerificationCodeExpiredError()
            
            await asyncio.gather(
                uow.client_repo.verify_client(verification_code.client.id), 
                uow.verification_code_repo.delete_verification_codes(verification_code.client.id)
            )
            
    async def refresh(self, raw_refresh_token: str) -> tuple[str, str]: 
        stored = await self._get_valid_refresh(raw_refresh_token)
        client = await self._get_client_for_token(stored.client_id)
        
        async with UnitOfWork() as uow:
            await uow.refresh_token_repo.revoke_refresh_token_by_hash(stored.token_hash)
            
        pair = await self._issue_token(client.id)
        return pair
        
    async def _get_valid_refresh(self, raw_refresh_token: str) -> RefreshToken: 
        # Hash refresh token
        token_hash = tokens.hash_token(raw_refresh_token)
        
        # Init refresh token repo
        async with UnitOfWork() as uow:
            refresh_token = await uow.refresh_token_repo.get_refresh_token_by_hash(token_hash)
            
            # Validate
            if not refresh_token or refresh_token.revoked: 
                logger.error(f"Refresh token {token_hash} is revoked or not found")
                raise RefreshTokenNotFoundError()
            
            if refresh_token.expires_at <= datetime.now(timezone.utc):
                await uow.refresh_token_repo.revoke_refresh_token_by_hash(token_hash)
                logger.error(f"Refresh token {token_hash} has expired")
                raise RefreshTokenExpiredError()
        
        return refresh_token 
        
    async def _get_client_for_token(self, client_id: int) -> Client: 
        # Init Client Repo
        client_repo = ClientRepository(self.session)
        client = await client_repo.get_client_by_id(client_id)
        
        if not client: 
            logger.error(f"Client(id={client_id}) not found")
            raise ClientNotFoundError()
        
        return client
        
    async def _get_client_or_raise(self, email: str, password: str) -> Client: 
        # Init Client Repo
        client_repo = ClientRepository(self.session)
        client = await client_repo.get_client_by_email(email)
        
        # Verify password
        if not client or not security.verify_password(password, client.password_hash): 
            logger.error(f"Invalid credentials for Client(email={email})")
            raise InvalidCredentialsError()
        
        return client
    
    def _refresh_expiry(self) -> datetime: 
        return datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_MINUTES)
    
    async def _issue_token(self, client_id: int) -> tuple[str, str]: 
        # Issue tokens
        access_token = tokens.create_access_token(client_id)
        refresh_token = tokens.create_refresh_token()
        refresh_hash = tokens.hash_token(refresh_token)
        expires_at = self._refresh_expiry()
        
        # Save Refresh token hash
        async with UnitOfWork() as uow: 
            await uow.refresh_token_repo.create_refresh_token(client_id, refresh_hash, expires_at)

        return access_token, refresh_token
