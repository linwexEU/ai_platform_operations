from fastapi import APIRouter

from app.entrypoints.routers.client import router as client_router
from app.entrypoints.routers.auth import router as auth_router
from app.entrypoints.routers.session import router as session_router
from app.entrypoints.routers.document import router as document_router

router = APIRouter()

# Include all routers
router.include_router(client_router, prefix="/client", tags=["Clients"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(session_router, prefix="/session", tags=["Sessions"])
router.include_router(document_router, prefix="/document", tags=["Documents"])
