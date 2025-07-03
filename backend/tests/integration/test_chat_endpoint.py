import pytest
import json
from flask import Flask

@pytest.mark.integration
class TestChatEndpoint:
    """Integration tests for the chat endpoint."""

    def test_chat_endpoint_basic(self, client, mock_openai, mock_sentiment_analyzer, mock_language_detector):
        """Test the chat endpoint with basic functionality."""
        # Prepare the request data
        data = {
            "message": "Hello",
            "session_id": "test_session"
        }
        
        # Send the request
        response = client.post("/chat", json=data)
        
        # Verify the response
        assert response.status_code == 200
        assert "response" in response.json
        
        # Verify the response contains expected elements
        response_text = response.json["response"]
        assert "Mocked OpenAI response" in response_text
        assert "Catalan proverb" in response_text
        assert "Translation" in response_text

    def test_chat_endpoint_with_detected_language(self, client, mock_openai, mock_sentiment_analyzer):
        """Test the chat endpoint with a pre-detected language."""
        # Prepare the request data
        data = {
            "message": "Hola",
            "session_id": "test_session",
            "detected_language": "es"
        }
        
        # Send the request
        response = client.post("/chat", json=data)
        
        # Verify the response
        assert response.status_code == 200
        assert "response" in response.json
        
        # Verify the response contains expected elements
        response_text = response.json["response"]
        assert "Mocked OpenAI response" in response_text
        assert "Catalan proverb" in response_text
        assert "Traducción" in response_text  # Spanish translation label

    def test_chat_endpoint_with_feedback(self, client, mock_openai, mock_sentiment_analyzer, mock_language_detector):
        """Test the chat endpoint with feedback data."""
        # Prepare the request data with feedback
        data = {
            "message": "Hello",
            "session_id": "test_session",
            "feedback": [
                {
                    "query_id": "test_query",
                    "is_helpful": True,
                    "result_ids": ["result1", "result2"]
                }
            ]
        }
        
        # Send the request
        response = client.post("/chat", json=data)
        
        # Verify the response
        assert response.status_code == 200
        assert "response" in response.json

    def test_chat_endpoint_empty_message(self, client):
        """Test the chat endpoint with an empty message."""
        # Prepare the request data
        data = {
            "message": "",
            "session_id": "test_session"
        }
        
        # Send the request
        response = client.post("/chat", json=data)
        
        # Verify the response
        assert response.status_code == 400
        assert "error" in response.json
        assert "message" in response.json

    def test_chat_endpoint_invalid_json(self, client):
        """Test the chat endpoint with invalid JSON."""
        # Send the request with invalid JSON
        response = client.post("/chat", data="not json", content_type="application/json")
        
        # Verify the response
        assert response.status_code == 400
        assert "error" in response.json
        assert "message" in response.json

    def test_chat_endpoint_missing_message(self, client):
        """Test the chat endpoint with missing message field."""
        # Prepare the request data
        data = {
            "session_id": "test_session"
        }
        
        # Send the request
        response = client.post("/chat", json=data)
        
        # Verify the response
        assert response.status_code == 400
        assert "error" in response.json
        assert "message" in response.json

    def test_chat_endpoint_restaurant_trigger(self, client, mock_language_detector, mocker):
        """Test the chat endpoint with a restaurant trigger."""
        # Mock the restaurant trigger detection
        mocker.patch("app.services.restaurant_service.contains_restaurant_trigger", return_value=True)
        
        # Mock the restaurant dialog handler
        mocker.patch(
            "app.services.restaurant_service.handle_restaurant_dialog",
            return_value={"response": "Restaurant response"}
        )
        
        # Prepare the request data
        data = {
            "message": "I want to book a restaurant",
            "session_id": "test_session"
        }
        
        # Send the request
        response = client.post("/chat", json=data)
        
        # Verify the response
        assert response.status_code == 200
        assert "response" in response.json
        assert response.json["response"] == "Restaurant response"

    def test_chat_endpoint_request_id(self, client, mock_openai, mock_sentiment_analyzer, mock_language_detector):
        """Test that the chat endpoint includes a request ID in the response headers."""
        # Prepare the request data
        data = {
            "message": "Hello",
            "session_id": "test_session"
        }
        
        # Send the request with a request ID header
        response = client.post("/chat", json=data, headers={"X-Request-ID": "test-request-id"})
        
        # Verify the response
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] == "test-request-id"