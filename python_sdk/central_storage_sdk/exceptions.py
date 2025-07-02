"""
Custom exceptions for the Central Storage System SDK
"""

class APIError(Exception):
    """Base exception for API related errors"""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    pass

class PermissionError(APIError):
    """Raised when user doesn't have required permissions"""
    pass

class NotFoundError(APIError):
    """Raised when a resource is not found"""
    pass

class ValidationError(APIError):
    """Raised when request data is invalid"""
    pass
