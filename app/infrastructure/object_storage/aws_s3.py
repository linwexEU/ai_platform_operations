import asyncio
import logging
from functools import wraps
from typing import Coroutine, Any, Optional, Callable

import aioboto3
import botocore.exceptions as exc
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt

from app.domain.core.config import settings

logger = logging.getLogger(__name__)


def handle_error(coroutine: Coroutine) -> Callable: 
    @wraps(coroutine)
    async def wrapper(*args: Any, **kwargs: Any) -> Optional[Any]:
        try: 
            result = await coroutine(*args, **kwargs)
        except exc.NoCredentialsError as err:
            logger.error(f"S3 no credentials error: {str(err)}")
            raise
        except exc.PartialCredentialsError as err: 
            logger.error(f"S3 partial credentials error: {str(err)}")
            raise
        except exc.EndpointConnectionError as err: 
            logger.error(f"S3 endpoint connection error: {str(err)}")
            raise
        except exc.ConnectTimeoutError as err: 
            logger.error(f"S3 connection timeout error: {str(err)}")
            raise
        except exc.ReadTimeoutError as err: 
            logger.error(f"S3 read timeout error: {str(err)}")
            raise
        except exc.ConnectionClosedError as err: 
            logger.error(f"S3 connection closed error: {str(err)}")
            raise
        except exc.ClientError as err: 
            logger.error(f"S3 client error: {str(err)}")
            raise
        except exc.ParamValidationError as err: 
            logger.error(f"S3 param validation error: {str(err)}")
            raise
        except asyncio.TimeoutError as err: 
            logger.error(f"S3 asyncio timeout error: {str(err)}")
            raise
        except OSError as err: 
            logger.error(f"S3 OSError: {str(err)}")
            raise
        return result
    return wrapper


class ObjectStorage: 
    def __init__(self) -> None: 
        self.session = aioboto3.Session(**settings.AWS_CREDENTIALS)
    
    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=3, max=10), 
        retry=retry_if_exception_type(
            (
                exc.EndpointConnectionError, 
                exc.ConnectTimeoutError, 
                exc.ConnectionClosedError,
                exc.ReadTimeoutError
            )
        )
    )
    @handle_error
    async def read_file(self, key: str) -> bytes: 
        async with self.session.client("s3") as s3: 
            resp = await s3.get_object(Bucket=settings.AWS_BUCKET_NAME, Key=key)
            async with resp["Body"] as stream: 
                return await stream.read()
    
    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=3, max=10), 
        retry=retry_if_exception_type(
            (
                exc.EndpointConnectionError, 
                exc.ConnectTimeoutError, 
                exc.ConnectionClosedError,
                exc.ReadTimeoutError
            )
        )
    )
    @handle_error
    async def delete_file(self, key: str) -> None: 
        async with self.session.client("s3") as s3: 
            await s3.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=key) 
    
    @handle_error
    async def generate_file_link(self, key: str, expires: int = 300) -> str: 
        async with self.session.client("s3") as s3: 
            return await s3.generate_presigned_url(
                "get_object", 
                Params={"Bucket": settings.AWS_BUCKET_NAME, "Key": key}, 
                Expires=expires
            )
    
    @handle_error    
    async def generate_upload_link(self, key: str, expires: int = 300) -> str: 
        async with self.session.client("s3") as s3: 
            return await s3.generate_presigned_url(
                "put_object", 
                Params={"Bucket": settings.AWS_BUCKET_NAME, "Key": key}, 
                ExpiresIn=expires
            )
