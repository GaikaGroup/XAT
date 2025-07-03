import pytest
import json
from unittest.mock import patch

@pytest.mark.integration
class TestFeedbackRoutes:
    """Integration tests for the feedback routes."""

    @patch('backend.app.routes.feedback_routes.log_rag_feedback')
    def test_rag_feedback_success(self, mock_log_feedback, client):
        """Test the RAG feedback endpoint with valid data."""
        # Prepare the request data
        data = {
            "query_id": "test-query-id",
            "is_helpful": True,
            "result_ids": ["result1", "result2"]
        }
        
        # Send the request
        response = client.post("/feedback/rag", json=data)
        
        # Verify the response
        assert response.status_code == 200
        assert "status" in response.json
        assert response.json["status"] == "success"
        assert "message" in response.json
        assert "Feedback recorded successfully" in response.json["message"]
        assert "timestamp" in response.json
        
        # Verify that the log_rag_feedback function was called with the correct arguments
        mock_log_feedback.assert_called_once_with("test-query-id", True, ["result1", "result2"])

    def test_rag_feedback_not_json(self, client):
        """Test the RAG feedback endpoint with non-JSON data."""
        # Send the request with non-JSON data
        response = client.post("/feedback/rag", data="not json", content_type="application/json")
        
        # Verify the response
        assert response.status_code == 400
        assert "error" in response.json
        assert response.json["error"] == "Request must be JSON"

    def test_rag_feedback_invalid_json(self, client):
        """Test the RAG feedback endpoint with invalid JSON."""
        # Send the request with invalid JSON
        response = client.post("/feedback/rag", data="{", content_type="application/json")
        
        # Verify the response
        assert response.status_code == 400
        assert "error" in response.json
        assert "Invalid JSON" in response.json["error"]

    def test_rag_feedback_empty_json(self, client):
        """Test the RAG feedback endpoint with empty JSON."""
        # Send the request with empty JSON
        response = client.post("/feedback/rag", json=None)
        
        # Verify the response
        assert response.status_code == 400
        assert "error" in response.json
        assert response.json["error"] == "Invalid JSON"

    @patch('backend.app.routes.feedback_routes.log_rag_feedback', side_effect=Exception("Test error"))
    def test_rag_feedback_error(self, mock_log_feedback, client):
        """Test the RAG feedback endpoint when an error occurs."""
        # Prepare the request data
        data = {
            "query_id": "test-query-id",
            "is_helpful": True,
            "result_ids": ["result1", "result2"]
        }
        
        # Send the request
        response = client.post("/feedback/rag", json=data)
        
        # Verify the response
        assert response.status_code == 500
        assert "error" in response.json
        assert response.json["error"] == "Internal server error"
        assert "message" in response.json
        assert "Test error" in response.json["message"]
        
        # Verify that the log_rag_feedback function was called with the correct arguments
        mock_log_feedback.assert_called_once_with("test-query-id", True, ["result1", "result2"])

    def test_rag_feedback_options(self, client):
        """Test the RAG feedback endpoint with OPTIONS method (CORS preflight)."""
        # Send an OPTIONS request
        response = client.options("/feedback/rag")
        
        # Verify the response
        assert response.status_code == 200
        assert response.data == b""  # Empty response body
        
        # Verify CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers