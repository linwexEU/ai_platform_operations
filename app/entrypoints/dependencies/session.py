from typing import Annotated

from fastapi import Depends, Request

from app.entrypoints.dependencies.db import SessionDep
from app.services.session import SessionService


def get_session_service(request: Request, session: SessionDep) -> SessionService: 
    return SessionService(session, request.app.state["http_client"])


SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
