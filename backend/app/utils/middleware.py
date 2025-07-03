"""
Middleware for the application.

This module provides middleware functions for the Flask application,
including error handling and request ID tracking.
"""

import logging
import traceback
from functools import wraps
from typing import Callable, Dict, Any, Tuple, Optional
from flask import request, jsonify, Response, g, current_app

from utils.exceptions import APIError
from utils.request_id import generate_request_id, get_request_id, set_request_id

logger = logging.getLogger(__name__)

def error_handler(app):
    """
    Register an error handler for the application.
    
    Args:
        app: The Flask application
    """
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """
        Handle API errors by returning a JSON response with the error details.
        
        Args:
            error: The APIError that was raised
            
        Returns:
            Response: A JSON response with the error details
        """
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        
        # Add request ID to response headers
        request_id = get_request_id()
        if request_id:
            response.headers['X-Request-ID'] = request_id
            
        # Log the error
        logger.error(
            "API error: %s - %s - %s",
            error.error_code,
            error.message,
            error.details,
            exc_info=True
        )
        
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """
        Handle unhandled exceptions by returning a generic error response.
        
        Args:
            error: The exception that was raised
            
        Returns:
            Response: A JSON response with a generic error message
        """
        # Log the error with traceback
        logger.error(
            "Unhandled exception: %s\n%s",
            str(error),
            traceback.format_exc(),
            exc_info=True
        )
        
        # Create a generic error response
        response = jsonify({
            "error": "internal_error",
            "message": "An unexpected error occurred"
        })
        response.status_code = 500
        
        # Add request ID to response headers
        request_id = get_request_id()
        if request_id:
            response.headers['X-Request-ID'] = request_id
            
        return response

def request_id_middleware(app):
    """
    Register middleware to add request IDs to requests and responses.
    
    Args:
        app: The Flask application
    """
    @app.before_request
    def before_request():
        """
        Add a request ID to the request context before processing the request.
        """
        # Check if the request has a request ID header
        request_id = request.headers.get('X-Request-ID')
        
        # If not, generate a new request ID
        if not request_id:
            request_id = generate_request_id()
            
        # Set the request ID in the request context
        set_request_id(request_id)
        
        # Log the request
        logger.info(
            "Request: %s %s - Client: %s - Headers: %s",
            request.method,
            request.path,
            request.remote_addr,
            {k: v for k, v in request.headers.items() if k.lower() != 'authorization'}
        )
    
    @app.after_request
    def after_request(response):
        """
        Add the request ID to the response headers.
        
        Args:
            response: The response object
            
        Returns:
            Response: The modified response object
        """
        # Add request ID to response headers
        request_id = get_request_id()
        if request_id:
            response.headers['X-Request-ID'] = request_id
            
        # Log the response
        logger.info(
            "Response: %s - Headers: %s",
            response.status_code,
            {k: v for k, v in response.headers.items()}
        )
        
        return response

def register_middleware(app):
    """
    Register all middleware for the application.
    
    Args:
        app: The Flask application
    """
    # Register error handlers
    error_handler(app)
    
    # Register request ID middleware
    request_id_middleware(app)