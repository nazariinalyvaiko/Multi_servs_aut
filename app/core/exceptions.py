"""Custom exceptions and error handling."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

class BaseAPIException(Exception):
    """Base exception for API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """Validation error exception."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class AuthenticationError(BaseAPIException):
    """Authentication error exception."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(BaseAPIException):
    """Authorization error exception."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundError(BaseAPIException):
    """Not found error exception."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class ConflictError(BaseAPIException):
    """Conflict error exception."""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )


class RateLimitError(BaseAPIException):
    """Rate limit error exception."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class ServiceUnavailableError(BaseAPIException):
    """Service unavailable error exception."""
    
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class ExternalServiceError(BaseAPIException):
    """External service error exception."""
    
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"External service error ({service}): {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"service": service}
        )


def create_error_response(
    exception: BaseAPIException,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create standardized error response."""
    
    error_data = {
        "error": {
            "type": exception.__class__.__name__,
            "message": exception.message,
            "status_code": exception.status_code,
            "details": exception.details
        }
    }
    
    if request_id:
        error_data["error"]["request_id"] = request_id
    
    return JSONResponse(
        status_code=exception.status_code,
        content=error_data
    )


def handle_validation_error(exc: Exception) -> JSONResponse:
    """Handle Pydantic validation errors."""
    if hasattr(exc, 'errors'):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "Validation failed",
                    "status_code": 422,
                    "details": {"validation_errors": errors}
                }
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "ValidationError",
                "message": str(exc),
                "status_code": 422
            }
        }
    )
