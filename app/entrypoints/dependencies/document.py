from typing import Annotated

from fastapi import Depends

from app.services.document import DocumentService
from app.entrypoints.dependencies.object_storage import ObjectStorageDep
from app.entrypoints.dependencies.db import SessionDep


def get_document_service(session: SessionDep, object_storage: ObjectStorageDep) -> DocumentService: 
    return DocumentService(session, object_storage)


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
