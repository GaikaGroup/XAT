"""
Logging configuration for the application.

This module configures logging for the application, including structured logging
with proper log levels and request ID tracking.
"""

import logging
import sys
import os
from typing import Optional, Dict, Any
from flask import request, has_request_context

from utils.request_id import get_request_id

# Configure the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Create a formatter that includes the request ID
class RequestFormatter(logging.Formatter):
    """
    Custom formatter that includes the request ID in log messages.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record, adding request ID if available.
        
        Args:
            record: The log record to format
            
        Returns:
            str: The formatted log message
        """
        if has_request_context():
            record.request_id = get_request_id() or '-'
        else:
            record.request_id = '-'
            
        return super().format(record)

def configure_logging(app=None, log_level: str = "INFO") -> None:
    """
    Configure logging for the application.
    
    Args:
        app: The Flask application (optional)
        log_level: The log level to use (default: INFO)
    """
    # Set the log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create a formatter
    formatter = RequestFormatter(
        '%(asctime)s - %(name)s - [%(request_id)s] - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add the handler to the root logger
    root_logger.addHandler(console_handler)
    
    # Configure Flask logging if app is provided
    if app:
        # Set Flask logger level
        app.logger.setLevel(level)
        
        # Remove default Flask handlers
        for handler in app.logger.handlers:
            app.logger.removeHandler(handler)
        
        # Add our custom handler
        app.logger.addHandler(console_handler)
        
        # Log Flask errors
        @app.errorhandler(Exception)
        def handle_exception(e):
            app.logger.exception("Unhandled exception: %s", str(e))
            return {"error": "Internal server error"}, 500

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: The name of the logger
        
    Returns:
        logging.Logger: The logger
    """
    logger = logging.getLogger(name)
    return logger

def log_request_info(logger: logging.Logger) -> None:
    """
    Log information about the current request.
    
    Args:
        logger: The logger to use
    """
    if has_request_context():
        logger.info(
            "Request: %s %s - Headers: %s - Data: %s",
            request.method,
            request.path,
            {k: v for k, v in request.headers.items() if k.lower() != 'authorization'},
            request.get_json(silent=True)
        )

def log_response_info(logger: logging.Logger, response: Any) -> None:
    """
    Log information about the response.
    
    Args:
        logger: The logger to use
        response: The response object
    """
    if has_request_context():
        logger.info(
            "Response: %s - Headers: %s",
            response.status_code,
            {k: v for k, v in response.headers.items()}
        )