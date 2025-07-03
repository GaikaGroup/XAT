from flask import Blueprint, jsonify
import time

# Create a Blueprint for health routes
health_bp = Blueprint('health', __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Simple endpoint to check if the service is running.
    
    Returns:
        JSON response with status information
    """
    return jsonify({
        "status": "ok",
        "version": "1.1.0",
        "timestamp": time.time()
    }), 200

@health_bp.route("/", methods=["GET"])
def root():
    """
    Root endpoint that returns a welcome message.
    
    Returns:
        JSON response with welcome message and available endpoints
    """
    return jsonify({
        "message": "Welcome to HugDimon API!",
        "status": "online",
        "endpoints": {
            "/chat": "Send a message (POST)",
            "/guide": "Get information about places (POST)",
            "/health": "Check server status (GET)",
            "/metrics": "View metrics (GET)",
            "/feedback/rag": "Submit feedback on RAG results (POST)",
            "/admin/refresh-rag": "Refresh RAG index (POST, admin only)"
        },
        "version": "1.2.0"  # Updated version to reflect RAG improvements
    }), 200