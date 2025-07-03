import pytest
import json
from unittest.mock import patch

@pytest.mark.integration
class TestGuideRoutes:
    """Integration tests for the guide routes."""

    def test_guide_endpoint_with_rag_results(self, client, mock_rag_query_engine):
        """Test the guide endpoint when RAG returns results."""
        # Prepare the request data
        data = {
            "message": "Tell me about restaurants in Cadaqués"
        }
        
        # Send the request
        response = client.post("/guide", json=data)
        
        # Verify the response
        assert response.status_code == 200
        assert "response" in response.json
        
        # Verify the response contains expected elements from RAG results
        response_text = response.json["response"]
        assert "Mocked Restaurant" in response_text
        assert "Mocked RAG text" in response_text
        assert "Можно забронировать" in response_text
        assert "mock@example.com" in response_text
        assert "У этого места есть терраса" in response_text
        assert "Здесь открывается вид на море" in response_text

    @patch('backend.app.routes.guide_routes.query_places')
    def test_guide_endpoint_with_chatgpt_fallback(self, mock_query_places, client, mock_openai):
        """Test the guide endpoint when RAG returns no results and falls back to ChatGPT."""
        # Mock query_places to return empty results
        mock_query_places.return_value = []
        
        # Prepare the request data
        data = {
            "message": "Tell me about restaurants in Cadaqués"
        }
        
        # Send the request
        response = client.post("/guide", json=data)
        
        # Verify the response
        assert response.status_code == 200
        assert "response" in response.json
        
        # Verify the response contains expected elements from ChatGPT
        response_text = response.json["response"]
        assert "Mocked OpenAI response" in response_text

    def test_guide_endpoint_invalid_json(self, client):
        """Test the guide endpoint with invalid JSON."""
        # Send the request with invalid JSON
        response = client.post("/guide", data="not json", content_type="application/json")
        
        # Verify the response
        assert response.status_code == 400
        assert "error" in response.json
        assert "message" in response.json
        assert "Request must be JSON" in response.json["message"]

    def test_guide_endpoint_missing_message(self, client):
        """Test the guide endpoint with missing message field."""
        # Prepare the request data
        data = {}
        
        # Send the request
        response = client.post("/guide", json=data)
        
        # Verify the response
        assert response.status_code == 400
        assert "error" in response.json
        assert "message" in response.json
        assert "Missing message field" in response.json["message"]

    def test_guide_endpoint_empty_message(self, client):
        """Test the guide endpoint with empty message field."""
        # Prepare the request data
        data = {
            "message": ""
        }
        
        # Send the request
        response = client.post("/guide", json=data)
        
        # Verify the response
        assert response.status_code == 400
        assert "error" in response.json
        assert "message" in response.json
        assert "Empty message" in response.json["message"]

    @patch('backend.app.routes.guide_routes.query_places')
    def test_guide_endpoint_rag_error(self, mock_query_places, client):
        """Test the guide endpoint when RAG query raises an error."""
        # Mock query_places to raise an exception
        mock_query_places.side_effect = Exception("Test RAG error")
        
        # Prepare the request data
        data = {
            "message": "Tell me about restaurants in Cadaqués"
        }
        
        # Send the request
        response = client.post("/guide", json=data)
        
        # Verify the response
        assert response.status_code == 503
        assert "error" in response.json
        assert "message" in response.json
        assert "Error querying places database" in response.json["message"]

    @patch('backend.app.routes.guide_routes.query_places')
    @patch('backend.app.routes.guide_routes.get_chatgpt_response')
    def test_guide_endpoint_chatgpt_error(self, mock_get_chatgpt_response, mock_query_places, client):
        """Test the guide endpoint when ChatGPT raises an error."""
        # Mock query_places to return empty results
        mock_query_places.return_value = []
        
        # Mock get_chatgpt_response to raise an exception
        mock_get_chatgpt_response.side_effect = Exception("Test ChatGPT error")
        
        # Prepare the request data
        data = {
            "message": "Tell me about restaurants in Cadaqués"
        }
        
        # Send the request
        response = client.post("/guide", json=data)
        
        # Verify the response
        assert response.status_code == 502
        assert "error" in response.json
        assert "message" in response.json
        assert "Error getting AI response" in response.json["message"]

    def test_guide_endpoint_request_id(self, client, mock_rag_query_engine):
        """Test that the guide endpoint includes a request ID in the response headers."""
        # Prepare the request data
        data = {
            "message": "Tell me about restaurants in Cadaqués"
        }
        
        # Send the request with a request ID header
        response = client.post("/guide", json=data, headers={"X-Request-ID": "test-request-id"})
        
        # Verify the response
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] == "test-request-id"