from app.domain.exceptions.base import AppError


class VerificationCodeNotFoundError(AppError):
    """Verification Code Not Found Error"""
    pass 


class VerificationCodeExpiredError(AppError): 
    """Verification Code Expired Error"""
    pass 
