from app.domain.exceptions.base import AppError


class ClientNotFoundError(AppError): 
    """Client Not Found Error"""
    pass


class ClientAlreadyExistsError(AppError): 
    """Client Already Exists Error"""
    pass 
