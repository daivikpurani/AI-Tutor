"""
Custom exceptions for the application.
"""


class AppException(Exception):
    """Base exception for application errors."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseException(AppException):
    """Exception for database-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ValidationException(AppException):
    """Exception for validation errors."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundException(AppException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str, resource_id: str):
        message = f"{resource} with ID {resource_id} not found"
        super().__init__(message, status_code=404)


class FileProcessingException(AppException):
    """Exception for file processing errors."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class GradingException(AppException):
    """Exception for grading-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class LLMException(AppException):
    """Exception for LLM API errors."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=502)


class VectorStoreException(AppException):
    """Exception for vector store errors."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
