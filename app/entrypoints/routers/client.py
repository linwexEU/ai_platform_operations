from fastapi import APIRouter, HTTPException, status

from app.domain.exceptions.client import ClientAlreadyExistsError
from app.entrypoints.dependencies.auth import CurrClientDep
from app.entrypoints.dependencies.client import ClientServiceDep
from app.entrypoints.schemas.client import (
    RegisterClientRequest,
    RegisterClientResponse, 
    GetClientResponse
)

router = APIRouter()


@router.post("/registration")
async def register_client(payload: RegisterClientRequest, service: ClientServiceDep) -> RegisterClientResponse: 
    try:
        client = await service.register_client(
            payload.first_name, 
            payload.role, 
            payload.email, 
            payload.password, 
            payload.last_name
        ) 
    except ClientAlreadyExistsError: 
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Client with email '{payload.email}' already exists")
    return RegisterClientResponse(client_id=client.id)


@router.get("/me")
async def get_info(curr_client: CurrClientDep) -> GetClientResponse: 
    return curr_client
