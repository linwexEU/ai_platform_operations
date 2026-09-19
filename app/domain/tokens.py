from datetime import datetime, timezone, timedelta
import hashlib
import secrets
from typing import Any

import jwt

from app.domain.config import settings
from app.domain.exceptions.tokens import (
    TokenExpiredError,
    InvalidTokenIssuerError,
    InvalidTokenError,
    InvalidTokenTypeError,
    InvalidClientIdTokenError
)


class Tokens:
    def create_access_token(self, client_id: int) -> str: 
        return self._create_token(client_id, "access", settings.ACCESS_TOKEN_EXPIRES_MINUTES)
    
    def create_refresh_token(self) -> str: 
        return secrets.token_urlsafe(32) 
    
    def hash_token(self, token: str) -> str: 
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
    
    def decode_token(self, token: str, expected_type: str) -> dict[str, Any]: 
        try: 
            payload = jwt.decode(
                token,
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM], 
                issuer=settings.APP_NAME,
                options={
                    "require": ["sub", "type", "iat", "exp", "iss"]
                }
            )
        except jwt.ExpiredSignatureError: 
            raise TokenExpiredError()
        except jwt.InvalidIssuerError: 
            raise InvalidTokenIssuerError()
        except jwt.DecodeError(): 
            raise InvalidTokenError()
        
        if payload.get("type") != expected_type: 
            raise InvalidTokenTypeError()
        
        try:
            client_id = int(payload["sub"])
            if client_id < 0: 
                raise InvalidClientIdTokenError()
        except (ValueError, KeyError):
            raise InvalidClientIdTokenError()
        
        return payload
    
    def _create_token(self, client_id: int, token_type: str, expires_minutes: int) -> str: 
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(client_id),
            "type": token_type,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
            "iss": settings.APP_NAME
        } 
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    

tokens = Tokens()
