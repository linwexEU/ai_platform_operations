from app.domain.exceptions.base import AppError


class TokenExpiredError(AppError):
    """Token Expired Error"""
    pass


class InvalidTokenIssuerError(AppError): 
    """Invalid Token Issuer Error"""
    pass 


class InvalidTokenError(AppError): 
    """Invalid Token Error"""
    pass 


class InvalidTokenTypeError(AppError): 
    """Invalid Token Type Error"""
    pass 


class InvalidUserIdTokenError(AppError): 
    """Invalid User Id Token Error"""
    pass 
