from pydantic import BaseModel, EmailStr

from app.domain.core.enums import Role


class RegisterClientRequest(BaseModel): 
    first_name: str
    last_name: str | None = None
    email: EmailStr
    password: str
    role: Role


class RegisterClientResponse(BaseModel): 
    client_id: int


class GetClientResponse(BaseModel): 
    first_name: str
    last_name: str | None = None
    email: EmailStr
    role: Role 
    activated: bool
