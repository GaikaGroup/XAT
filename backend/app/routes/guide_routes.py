from flask import Blueprint, request, jsonify, Response
import logging
from typing import Tuple, Dict, Any, List, Optional

from services.restaurant_service import query_places, create_rag_response
from services.chatgpt_service import get_chatgpt_response
from utils.exceptions import BadRequestError, ValidationError, ServiceUnavailableError, ExternalServiceError
from utils.request_id import get_request_id
from services.chat_service import ChatService

# Configure logging
logger = logging.getLogger(__name__)

# Create a Blueprint for guide routes
guide_bp = Blueprint('guide', __name__)

@guide_bp.route("/guide", methods=["POST"])
def guide() -> Tuple[Response, int]:
    """
    Endpoint to get information about places in Cadaqués.

    This endpoint accepts a POST request with a JSON body containing a message field.
    It first tries to get results from the RAG (Retrieval-Augmented Generation) system.
    If results are found, it formats them into a response. Otherwise, it falls back to
    using ChatGPT to generate a response.

    Request JSON format:
        {
            "message": "string"  # The user's query about places in Cadaqués
        }

    Returns:
        Tuple[Response, int]: A tuple containing:
            - A JSON response with information about places
            - HTTP status code (200 for success, various error codes for failures)

    Raises:
        BadRequestError: If the request is not JSON or the message is empty
        ValidationError: If the message field is missing or invalid
        ServiceUnavailableError: If the RAG system is unavailable
        ExternalServiceError: If ChatGPT is unavailable
    """
    try:
        # 1. Ensure the request is JSON
        if not request.is_json:
            raise BadRequestError("Request must be JSON")

        data = request.get_json()

        # Validate message field exists
        if "message" not in data:
            raise ValidationError("Missing message field", {"field": "message"})

        # Get and sanitize user input
        user_input = data.get("message", "")

        # Validate and sanitize input
        try:
            user_input = ChatService.sanitize_input(user_input)
        except ValueError as e:
            raise ValidationError(str(e), {"field": "message"})

        if not user_input:
            raise ValidationError("Empty message", {"field": "message"})

        # Log the request
        logger.info(f"Guide request: {user_input[:50]}...")

        # 2. First, try to get results from RAG
        try:
            rag_results = query_places(user_input)
        except Exception as e:
            logger.error(f"Error querying RAG: {e}", exc_info=True)
            raise ServiceUnavailableError("Error querying places database", {"error": str(e)})

        if rag_results:
            # 3. If RAG found results, format the response
            logger.info(f"RAG found {len(rag_results)} results")
            response_text = create_rag_response(rag_results)

            # Prepare response
            response = jsonify({"response": response_text})

            # Add request ID to response headers
            request_id = get_request_id()
            if request_id:
                response.headers['X-Request-ID'] = request_id

            return response, 200

        # 4. If RAG finds nothing, fallback to ChatGPT
        logger.info("No RAG results found, falling back to ChatGPT")
        try:
            chatgpt_response = get_chatgpt_response(user_input, detected_lang='en')
        except Exception as e:
            logger.error(f"Error getting ChatGPT response: {e}", exc_info=True)
            raise ExternalServiceError("Error getting AI response", {"error": str(e)})

        # Prepare response
        response = jsonify({"response": chatgpt_response})

        # Add request ID to response headers
        request_id = get_request_id()
        if request_id:
            response.headers['X-Request-ID'] = request_id

        return response, 200

    except BadRequestError as e:
        logger.warning(f"Bad request: {e.message}", extra={"details": e.details})
        return jsonify(e.to_dict()), e.status_code

    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}", extra={"details": e.details})
        return jsonify(e.to_dict()), e.status_code

    except ServiceUnavailableError as e:
        logger.error(f"Service unavailable: {e.message}", extra={"details": e.details}, exc_info=True)
        return jsonify(e.to_dict()), e.status_code

    except ExternalServiceError as e:
        logger.error(f"External service error: {e.message}", extra={"details": e.details}, exc_info=True)
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        logger.error(f"Unhandled exception in /guide endpoint: {e}", exc_info=True)
        error_response = {
            "error": "internal_error",
            "message": "An unexpected error occurred"
        }

        # Add request ID to error response
        request_id = get_request_id()
        if request_id:
            error_response["request_id"] = request_id

        return jsonify(error_response), 500
