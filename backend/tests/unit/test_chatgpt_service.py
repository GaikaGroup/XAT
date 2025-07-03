import pytest
from unittest.mock import MagicMock, patch

from app.services.chatgpt_service import get_chatgpt_response, response_cache

class TestChatGPTService:
    """Tests for the ChatGPT service."""

    def test_get_chatgpt_response_basic(self, mock_openai):
        """Test the get_chatgpt_response function with basic functionality."""
        # Call the function
        response = get_chatgpt_response("Hello", "en")

        # Verify the response
        assert response == "Mocked OpenAI response"
        
        # Verify the OpenAI client was called correctly
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_client.chat.completions.create.call_args[1]
        assert call_args["model"] == "gpt-3.5-turbo"
        assert len(call_args["messages"]) == 2
        assert call_args["messages"][1]["content"] == "Hello"

    def test_get_chatgpt_response_with_context(self, mock_openai):
        """Test the get_chatgpt_response function with context."""
        # Call the function with context
        response = get_chatgpt_response("Hello", "en", context="Test context")

        # Verify the response
        assert response == "Mocked OpenAI response"
        
        # Verify the OpenAI client was called correctly
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_client.chat.completions.create.call_args[1]
        assert "Test context" in call_args["messages"][0]["content"]

    def test_get_chatgpt_response_caching(self, mock_openai):
        """Test that responses are cached."""
        # Clear the cache
        response_cache.clear()
        
        # Call the function twice with the same input
        response1 = get_chatgpt_response("Hello", "en")
        response2 = get_chatgpt_response("Hello", "en")
        
        # Verify both responses are the same
        assert response1 == response2
        
        # Verify the OpenAI client was called only once
        mock_client = mock_openai.return_value
        assert mock_client.chat.completions.create.call_count == 1

    def test_get_chatgpt_response_different_languages(self, mock_openai):
        """Test that different languages use different cache keys."""
        # Clear the cache
        response_cache.clear()
        
        # Call the function with different languages
        response_en = get_chatgpt_response("Hello", "en")
        response_es = get_chatgpt_response("Hello", "es")
        
        # Verify the OpenAI client was called twice
        mock_client = mock_openai.return_value
        assert mock_client.chat.completions.create.call_count == 2

    @patch("app.services.chatgpt_service.translate_text")
    def test_get_chatgpt_response_rate_limit_error(self, mock_translate, mock_openai):
        """Test handling of rate limit errors."""
        # Configure the mock to raise a rate limit error
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.side_effect = Exception("RateLimitError")
        
        # Configure the translate mock
        mock_translate.return_value = "Translated fallback"
        
        # Call the function
        response = get_chatgpt_response("Hello", "en")
        
        # Verify the fallback response was used
        assert response == "Translated fallback"
        mock_translate.assert_called_once()

    @patch("app.services.chatgpt_service.translate_text")
    def test_get_chatgpt_response_timeout_error(self, mock_translate, mock_openai):
        """Test handling of timeout errors."""
        # Configure the mock to raise a timeout error
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.side_effect = Exception("APITimeoutError")
        
        # Configure the translate mock
        mock_translate.return_value = "Translated fallback"
        
        # Call the function
        response = get_chatgpt_response("Hello", "en")
        
        # Verify the fallback response was used
        assert response == "Translated fallback"
        mock_translate.assert_called_once()

    @patch("app.services.chatgpt_service.translate_text")
    def test_get_chatgpt_response_general_error(self, mock_translate, mock_openai):
        """Test handling of general errors."""
        # Configure the mock to raise a general error
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.side_effect = Exception("General error")
        
        # Configure the translate mock
        mock_translate.return_value = "Translated fallback"
        
        # Call the function
        response = get_chatgpt_response("Hello", "en")
        
        # Verify the fallback response was used
        assert response == "Translated fallback"
        mock_translate.assert_called_once()

    @patch("app.services.chatgpt_service.log_metric")
    def test_get_chatgpt_response_metrics(self, mock_log_metric, mock_openai):
        """Test that metrics are logged."""
        # Clear the cache
        response_cache.clear()
        
        # Call the function
        get_chatgpt_response("Hello", "en")
        
        # Verify metrics were logged
        assert mock_log_metric.call_count > 0