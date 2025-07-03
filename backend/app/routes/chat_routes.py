from flask import Blueprint, request, jsonify, Response
import asyncio
import logging
from typing import Tuple

from services.chat_service import ChatService
from utils.exceptions import BadRequestError, ValidationError, ServiceUnavailableError
from utils.request_id import get_request_id

# Configure logging
logger = logging.getLogger(__name__)

# Create a Blueprint for chat routes
chat_bp = Blueprint('chat', __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat() -> Tuple[Response, int]:
    """
    Process user input, generate an AI response, select a proverb, and translate if necessary.

    This endpoint accepts a POST request with a JSON body containing a message field.
    It processes the user's input, detects the language, analyzes sentiment, generates
    a response using ChatGPT, adds a Catalan proverb based on sentiment, and translates
    the proverb if necessary.

    Request JSON format:
        {
            "message": "string",                  # Required: The user's message
            "session_id": "string",               # Optional: Session ID for tracking conversations
            "detected_language": "string",        # Optional: Pre-detected language code
            "feedback": [                         # Optional: Feedback on previous responses
                {
                    "query_id": "string",
                    "is_helpful": boolean,
                    "result_ids": ["string"]
                }
            ]
        }

    Returns:
        Tuple[Response, int]: A tuple containing:
            - A JSON response with the generated text
            - HTTP status code (200 for success, various error codes for failures)

    Raises:
        BadRequestError: If the request is not JSON or the JSON is invalid
        ValidationError: If required fields are missing or invalid
        ServiceUnavailableError: If there's an error processing the request
    """
    try:
        # Request validation
        if not request.is_json:
            raise BadRequestError("Request must be JSON")

        data = request.get_json()
        if not data:
            raise BadRequestError("Invalid JSON")

        # Validate required fields
        if "message" not in data:
            raise ValidationError("Missing message field", {"field": "message"})

        # Get input parameters
        user_input = data.get("message", "")
        session_id = data.get("session_id", "unknown")
        detected_language = data.get("detected_language")

        # Sanitize user input
        try:
            user_input = ChatService.sanitize_input(user_input)
        except ValueError as e:
            raise ValidationError(str(e), {"field": "message"})

        # Validate session_id
        if session_id and not isinstance(session_id, str):
            raise ValidationError("Session ID must be a string", {"field": "session_id"})

        # Validate detected_language if provided
        if detected_language and not isinstance(detected_language, str):
            raise ValidationError("Detected language must be a string", {"field": "detected_language"})

        # Process any feedback data included in the request
        feedback_data = data.get("feedback", [])
        if feedback_data and isinstance(feedback_data, list):
            from metrics.inference_metrics import log_rag_feedback

            feedback_count = len(feedback_data)
            logger.info(f"Processing {feedback_count} feedback items from chat request")

            for item in feedback_data:
                try:
                    query_id = item.get("query_id", "")
                    is_helpful = item.get("is_helpful", False)
                    result_ids = item.get("result_ids", [])

                    # Log the feedback
                    log_rag_feedback(query_id, is_helpful, result_ids)
                    logger.info(f"Processed feedback: query_id={query_id}, is_helpful={is_helpful}")
                except Exception as e:
                    logger.error(f"Error processing feedback item: {e}", exc_info=True)
                    # Continue processing other feedback items
                    continue

            logger.info(f"Successfully processed {feedback_count} feedback items")

        if not user_input:
            raise ValidationError("Empty message", {"field": "message"})

        # Sanitize input
        user_input = ChatService.sanitize_input(user_input)
        logger.info(f"Received chat request: {user_input[:50]}... (detected language: {detected_language or 'not specified'})")

        # Process the request asynchronously
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(ChatService.process_request_async(user_input, session_id, detected_language))
            loop.close()
        except RuntimeError as e:
            if "There is no current event loop" in str(e):
                # Handle the case where the event loop is closed
                logger.warning("No event loop available, creating new one")
                asyncio.set_event_loop(asyncio.new_event_loop())
                result = asyncio.get_event_loop().run_until_complete(ChatService.process_request_async(user_input, session_id, detected_language))
            else:
                logger.error(f"Runtime error in async processing: {e}", exc_info=True)
                raise ServiceUnavailableError("Error processing request", {"error": str(e)})
        except Exception as e:
            logger.error(f"Error in async processing: {e}", exc_info=True)
            raise ServiceUnavailableError("Error processing request", {"error": str(e)})

        # Prepare response
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'

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

    except Exception as e:
        logger.error(f"Unhandled exception in /chat endpoint: {e}", exc_info=True)
        error_response = {
            "error": "internal_error",
            "message": "An unexpected error occurred"
        }

        # Add request ID to error response
        request_id = get_request_id()
        if request_id:
            error_response["request_id"] = request_id

        return jsonify(error_response), 500
