from flask import Blueprint, request, jsonify
import logging
import time
from flask_cors import cross_origin

from metrics.inference_metrics import log_rag_feedback

# Configure logging
logger = logging.getLogger(__name__)

# Create a Blueprint for feedback routes
feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route("/feedback/rag", methods=["POST", "OPTIONS"])
@cross_origin(supports_credentials=True)
def rag_feedback():
    """
    Endpoint to collect user feedback on RAG results.
    
    Returns:
        JSON response with status information
    """
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return "", 200  # Return empty response with 200 OK for preflight

    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        # Extract feedback data
        query_id = data.get("query_id", "")
        is_helpful = data.get("is_helpful", False)
        result_ids = data.get("result_ids", [])

        # Log the feedback
        log_rag_feedback(query_id, is_helpful, result_ids)

        logger.info(f"Received RAG feedback: query_id={query_id}, is_helpful={is_helpful}, results={len(result_ids)}")

        return jsonify({
            "status": "success",
            "message": "Feedback recorded successfully",
            "timestamp": time.time()
        }), 200

    except Exception as e:
        logger.error(f"Error recording RAG feedback: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500