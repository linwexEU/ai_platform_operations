from app.domain.exceptions.base import AppError


class EmbeddingDimensionError(AppError): 
    """Embedding Dimension Error"""
    pass 


class EmbeddingValueError(AppError): 
    """Embedding Value Error"""
    pass 
