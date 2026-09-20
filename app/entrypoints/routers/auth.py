from fastapi import APIRouter, HTTPException, Response, status
from pydantic import EmailStr

from app.domain.core.config import settings
from app.domain.exceptions.base import AppError
from app.domain.exceptions.client import ClientNotFoundError
from app.domain.exceptions.tokens import (
    InvalidCredentialsError, 
    RefreshTokenExpiredError, 
    RefreshTokenNotFoundError 
)
from app.domain.exceptions.verification_code import (
    VerificationCodeNotFoundError,
    VerificationCodeExpiredError
)
from app.entrypoints.dependencies.auth import AuthServiceDep
from app.entrypoints.schemas.auth import (
    LoginRequest,
    TokenPair,
    RefreshRequest
)

router = APIRouter()


def _set_token_cookie(response: Response, access_token: str, refresh_token: str) -> None: 
    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True, 
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax", 
        max_age=settings.ACCESS_TOKEN_EXPIRES_MINUTES * 60
    ) 
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax", 
        max_age=settings.REFRESH_TOKEN_EXPIRES_MINUTES * 60
    )


@router.post("/login")
async def login(payload: LoginRequest, response: Response, service: AuthServiceDep) -> TokenPair: 
    try:
        access_token, refresh_token = await service.login(payload.email, payload.password) 
    except InvalidCredentialsError as err: 
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(err)) from err
    except AppError as err:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(err)) from err
    _set_token_cookie(response, access_token, refresh_token)
    return TokenPair(
        access_token=access_token, 
        refresh_token=refresh_token
    )


@router.post("/token/refresh")
async def refresh_tokens(payload: RefreshRequest, response: Response, service: AuthServiceDep) -> TokenPair: 
    try:
        access_token, refresh_token = await service.refresh(payload.refresh_token)
    except RefreshTokenExpiredError as err:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(err)) from err
    except RefreshTokenNotFoundError as err: 
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(err)) from err
    except ClientNotFoundError as err: 
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(err)) from err
    except AppError as err: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err
    _set_token_cookie(response, access_token, refresh_token)
    return TokenPair(
        access_token=access_token, 
        refresh_token=refresh_token
    )


@router.post("/verification/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def verify_account(code: str, email: EmailStr, service: AuthServiceDep) -> None: 
    try:
        await service.verify_account(code, email) 
    except VerificationCodeNotFoundError: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification code not found")
    except VerificationCodeExpiredError: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code has expired")
    except InvalidCredentialsError as err:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(err)) from err
