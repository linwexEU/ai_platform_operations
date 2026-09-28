from abc import ABC, abstractmethod 


class AbstractHttpClient(ABC): 
    @abstractmethod
    async def download(self, url: str, filename: str, chunk_size: int = 64 * 1024) -> None: ...
    