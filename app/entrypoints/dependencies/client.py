from typing import Annotated

from fastapi import Depends

from app.services.client import ClientService


def get_client_service() -> ClientService: 
    return ClientService()


ClientServiceDep = Annotated[ClientService, Depends(get_client_service)]
