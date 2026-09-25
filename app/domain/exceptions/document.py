from app.domain.exceptions.base import AppError


class InvalidDocumentMimeTypeError(AppError): 
    """Invalid Document Mime Type Error"""
    pass 


class ExceededDocumentSizeError(AppError): 
    """Exceeded Document Size Error"""
    pass 


class DocumentNotFoundError(AppError): 
    """Document Not Found Error"""
    pass 
