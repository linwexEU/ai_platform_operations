from typing import Annotated 

from fastapi import Depends, Request, HTTPException, status

from app.domain.core.tokens import tokens
from app.entrypoints.dependencies.db import SessionDep
from app.services.auth import AuthService
from app.infrastructure.database.models import Client
from app.infrastructure.repositories.client import ClientRepository
from app.domain.core.config import settings
from app.domain.exceptions.tokens import (
    TokenExpiredError,
    InvalidTokenIssuerError,
    InvalidTokenError,
    InvalidTokenTypeError,
    InvalidClientIdTokenError
)


def get_auth_service(session: SessionDep) -> AuthService: 
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_client_from_bearer(request: Request, session: SessionDep) -> Client: 
    raw_token = _extract_access_token(request)
    try:
        payload = tokens.decode_token(raw_token, "access")
    except TokenExpiredError: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") 
    except InvalidTokenIssuerError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token issuer")  
    except InvalidTokenError: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") 
    except InvalidTokenTypeError: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")  
    except InvalidClientIdTokenError: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid client id token")
    
    # Get client
    client_repo = ClientRepository(session)
    client = await client_repo.get_client_by_id(int(payload["sub"]))
    
    # Check client exists
    if not client: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Client id not found")
    
    return client


CurrClientDep = Annotated[Client, Depends(get_current_client_from_bearer)]


async def get_current_activated_client(curr_client: CurrClientDep) -> Client: 
    if not curr_client.activated: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account is not activated")

    return curr_client


CurrActivatedClient = Annotated[Client, Depends(get_current_activated_client)]



def _extract_access_token(request: Request) -> str: 
    header = request.headers.get("authorization") 
    if header and header.lower().startswith("bearer "): 
        return header.split(" ", 1)[1].strip()
    cookie_token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
    if cookie_token: 
        return cookie_token
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")
