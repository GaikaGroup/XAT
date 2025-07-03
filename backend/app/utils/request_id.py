"""
Request ID tracking utilities.

This module provides utilities for generating and tracking request IDs,
which are used to correlate log messages and responses for a single request.
"""

import uuid
import logging
from typing import Optional
from flask import request, g, has_request_context

logger = logging.getLogger(__name__)

def generate_request_id() -> str:
    """
    Generate a unique request ID.
    
    Returns:
        str: A unique request ID
    """
    return str(uuid.uuid4())

def get_request_id() -> Optional[str]:
    """
    Get the current request ID from the Flask request context.
    
    Returns:
        Optional[str]: The current request ID, or None if not in a request context
    """
    if has_request_context():
        # First check if it's in the request headers
        request_id = request.headers.get('X-Request-ID')
        if request_id:
            return request_id
        
        # Then check if it's in the Flask g object
        if hasattr(g, 'request_id'):
            return g.request_id
    
    return None

def set_request_id(request_id: Optional[str] = None) -> str:
    """
    Set the request ID in the Flask request context.
    
    Args:
        request_id: The request ID to set, or None to generate a new one
        
    Returns:
        str: The request ID that was set
    """
    if not has_request_context():
        logger.warning("Attempted to set request ID outside of request context")
        return generate_request_id()
    
    if request_id is None:
        request_id = generate_request_id()
    
    g.request_id = request_id
    return request_id