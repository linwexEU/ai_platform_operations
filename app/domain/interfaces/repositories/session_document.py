from abc import ABC, abstractmethod


class AbstractSessionDocumentRepository(ABC): 
    @abstractmethod
    async def attach_document_to_session(self, session_id: int, document_id: int) -> None: ...
    
    @abstractmethod
    async def detach_document_from_session(self, session_id: int, document_id: int) -> None: ...
