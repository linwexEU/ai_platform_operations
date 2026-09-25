from typing import Annotated

from fastapi import Depends

from app.infrastructure.object_storage.aws_s3 import ObjectStorage

object_storage = ObjectStorage()


def get_object_storage() -> ObjectStorage: 
    return object_storage


ObjectStorageDep = Annotated[ObjectStorage, Depends(get_object_storage)]
