from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.domain.core.config import settings


def document_splitter(document_text: str) -> list[str]: 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE, 
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return text_splitter.split_text(document_text)
