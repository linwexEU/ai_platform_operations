from typing import Annotated

from fastapi import Depends

from app.entrypoints.dependencies.db import SessionDep
from app.services.session import SessionService


def get_session_service(session: SessionDep) -> SessionService: 
    return SessionService(session)


SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
