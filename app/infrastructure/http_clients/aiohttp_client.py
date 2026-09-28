import logging
import pathlib

import aiohttp
import aiofiles
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.domain.core.config import settings
from app.domain.interfaces.http_clients.base import AbstractHttpClient

logger = logging.getLogger(__name__)


class HttpClient(AbstractHttpClient):    
    def __init__(self) -> None: 
        self.session: aiohttp.ClientSession | None = None
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10, multiplier=1), 
        retry=retry_if_exception_type(
            (
                aiohttp.ClientConnectorError,
                aiohttp.ServerTimeoutError
            )
        )
    )   
    async def download(self, url: str, filename: str, chunk_size: int = 64 * 1024) -> None:
        # Create session 
        await self.create_session()
        
        # Download file
        try:
            async with self.session.get(url) as response: 
                response.raise_for_status()
                async with aiofiles.open(pathlib.Path(settings.TEMP_FOLDER_PATH) / pathlib.Path(filename), "wb") as file: 
                    while chunk := await response.content.read(chunk_size): 
                        await file.write(chunk)
        except aiohttp.ClientConnectorError as err: 
            logger.error(f"HTTP client connection error: {str(err)}") 
            raise
        except aiohttp.ClientResponseError as err: 
            logger.error(f"HTTP client response: {response.status} error: {str(err)}")
            
            if response.status >= 500:
                raise aiohttp.ServerTimeoutError()
            raise
        except aiohttp.ServerTimeoutError as err: 
            logger.error(f"HTTP server timeout error: {str(err)}")
            raise
        except aiohttp.ClientPayloadError as err: 
            logger.error(f"HTTP client payload error: {str(err)}")
            raise
    
    async def create_session(self) -> None: 
        if self.session is None: 
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            
    async def close_session(self) -> None: 
        if self.session: 
            await self.session.close()
