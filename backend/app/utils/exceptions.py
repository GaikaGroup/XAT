"""
Custom exceptions for the application.

This module defines custom exception classes that can be raised by the application
to indicate specific error conditions. Each exception class corresponds to a specific
HTTP status code and error message.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for all API errors."""
    
    status_code = 500
    error_code = "internal_error"
    default_message = "An unexpected error occurred"
    
    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the API error.
        
        Args:
            message: A human-readable error message
            details: Additional details about the error
        """
        self.message = message or self.default_message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error to a dictionary that can be returned as JSON.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the error
        """
        error_dict = {
            "error": self.error_code,
            "message": self.message
        }
        
        if self.details:
            error_dict["details"] = self.details
            
        return error_dict

class BadRequestError(APIError):
    """Exception raised when the request is malformed or invalid."""
    
    status_code = 400
    error_code = "bad_request"
    default_message = "The request was invalid or malformed"

class ValidationError(BadRequestError):
    """Exception raised when request validation fails."""
    
    error_code = "validation_error"
    default_message = "The request data failed validation"

class AuthenticationError(APIError):
    """Exception raised when authentication fails."""
    
    status_code = 401
    error_code = "authentication_error"
    default_message = "Authentication failed"

class AuthorizationError(APIError):
    """Exception raised when the user is not authorized to perform an action."""
    
    status_code = 403
    error_code = "authorization_error"
    default_message = "You are not authorized to perform this action"

class NotFoundError(APIError):
    """Exception raised when a requested resource is not found."""
    
    status_code = 404
    error_code = "not_found"
    default_message = "The requested resource was not found"

class RateLimitError(APIError):
    """Exception raised when the rate limit is exceeded."""
    
    status_code = 429
    error_code = "rate_limit_exceeded"
    default_message = "Rate limit exceeded"

class ServiceUnavailableError(APIError):
    """Exception raised when a service is unavailable."""
    
    status_code = 503
    error_code = "service_unavailable"
    default_message = "The service is currently unavailable"

class ExternalServiceError(APIError):
    """Exception raised when an external service returns an error."""
    
    status_code = 502
    error_code = "external_service_error"
    default_message = "An external service returned an error"