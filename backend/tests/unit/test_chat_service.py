import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

from app.services.chat_service import ChatService, TRANSLATION_LABELS, SUPPORTED_LANGS

class TestChatService:
    """Tests for the ChatService class."""

    def test_get_response(self):
        """Test the get_response method."""
        # Test with a known input
        response = ChatService.get_response("Hola")
        assert response == "¡Hola! ¿Cómo estás?"

        # Test with an unknown input
        response = ChatService.get_response("Unknown")
        assert response == "No entiendo el mensaje."

    def test_external_api_call(self):
        """Test the external_api_call method."""
        response = ChatService.external_api_call("Test message")
        assert response == "Simulación de respuesta de API externa"

    def test_sanitize_input(self):
        """Test the sanitize_input method."""
        # Test with normal input
        input_text = "Hello, world!"
        sanitized = ChatService.sanitize_input(input_text)
        assert sanitized == input_text

        # Test with control characters
        input_text = "Hello\x00, world!"
        sanitized = ChatService.sanitize_input(input_text)
        assert sanitized == "Hello, world!"

        # Test with long input
        input_text = "x" * 1000
        sanitized = ChatService.sanitize_input(input_text)
        assert len(sanitized) == 500
        assert sanitized == "x" * 500

        # Test with None input
        with pytest.raises(ValueError, match="Input text cannot be None"):
            ChatService.sanitize_input(None)

        # Test with non-string input
        with pytest.raises(ValueError, match="Input must be a string"):
            ChatService.sanitize_input(123)

    @pytest.mark.asyncio
    async def test_process_request_async_basic(self, mocker):
        """Test the process_request_async method with basic functionality."""
        # Mock dependencies
        mocker.patch("app.services.chat_service.track_session")
        mocker.patch("app.services.chat_service.analyze_sentiment", return_value="Positive")
        mocker.patch("app.services.chat_service.detect_language", return_value="en")
        mocker.patch("app.services.chat_service.contains_restaurant_trigger", return_value=False)
        mocker.patch("app.services.chat_service.extract_required_features", return_value={})
        mocker.patch("app.services.chat_service.query_places", return_value=[])
        mocker.patch("app.services.chat_service.get_chatgpt_response", return_value="GPT response")
        mocker.patch("app.services.chat_service.get_proverb_by_sentiment", 
                    return_value=("Catalan proverb", "English translation"))

        # Call the method
        result = await ChatService.process_request_async("Hello", "test_session")

        # Verify the result
        assert "response" in result
        assert "GPT response" in result["response"]
        assert "Catalan proverb" in result["response"]
        assert "English translation" in result["response"]

    @pytest.mark.asyncio
    async def test_process_request_async_restaurant_trigger(self, mocker):
        """Test the process_request_async method with restaurant trigger."""
        # Mock dependencies
        mocker.patch("app.services.chat_service.track_session")
        mocker.patch("app.services.chat_service.analyze_sentiment", return_value="Positive")
        mocker.patch("app.services.chat_service.detect_language", return_value="en")
        mocker.patch("app.services.chat_service.contains_restaurant_trigger", return_value=True)
        
        # Mock the restaurant dialog handler
        mock_handle_restaurant = AsyncMock(return_value={"response": "Restaurant response"})
        mocker.patch("app.services.chat_service.handle_restaurant_dialog", side_effect=mock_handle_restaurant)

        # Call the method
        result = await ChatService.process_request_async("I want to book a restaurant", "test_session")

        # Verify the result
        assert "response" in result
        assert result["response"] == "Restaurant response"
        mock_handle_restaurant.assert_called_once_with("I want to book a restaurant", "test_session", "en")

    @pytest.mark.asyncio
    async def test_process_request_async_with_rag_results(self, mocker):
        """Test the process_request_async method with RAG results."""
        # Mock dependencies
        mocker.patch("app.services.chat_service.track_session")
        mocker.patch("app.services.chat_service.analyze_sentiment", return_value="Positive")
        mocker.patch("app.services.chat_service.detect_language", return_value="en")
        mocker.patch("app.services.chat_service.contains_restaurant_trigger", return_value=False)
        mocker.patch("app.services.chat_service.extract_required_features", return_value={})
        
        # Create mock RAG results
        mock_rag_results = [
            {
                "name": "Test Restaurant",
                "category": "Restaurant",
                "text": "A nice restaurant",
                "features": {"has_terrace": True, "sea_view": True},
                "has_booking": True,
                "email": "test@example.com"
            }
        ]
        mocker.patch("app.services.chat_service.query_places", return_value=mock_rag_results)
        mocker.patch("app.services.chat_service.get_chatgpt_response", return_value="GPT response with RAG context")
        mocker.patch("app.services.chat_service.get_proverb_by_sentiment", 
                    return_value=("Catalan proverb", "English translation"))

        # Call the method
        result = await ChatService.process_request_async("Tell me about restaurants", "test_session")

        # Verify the result
        assert "response" in result
        assert "GPT response with RAG context" in result["response"]
        assert "Catalan proverb" in result["response"]
        assert "English translation" in result["response"]

    @pytest.mark.asyncio
    async def test_process_request_async_with_translation(self, mocker):
        """Test the process_request_async method with translation."""
        # Mock dependencies
        mocker.patch("app.services.chat_service.track_session")
        mocker.patch("app.services.chat_service.analyze_sentiment", return_value="Positive")
        mocker.patch("app.services.chat_service.detect_language", return_value="es")
        mocker.patch("app.services.chat_service.contains_restaurant_trigger", return_value=False)
        mocker.patch("app.services.chat_service.extract_required_features", return_value={})
        mocker.patch("app.services.chat_service.query_places", return_value=[])
        mocker.patch("app.services.chat_service.get_chatgpt_response", return_value="GPT response")
        mocker.patch("app.services.chat_service.get_proverb_by_sentiment", 
                    return_value=("Catalan proverb", "English translation"))
        mocker.patch("app.services.chat_service.translate_text", return_value="Spanish translation")

        # Call the method
        result = await ChatService.process_request_async("Hola", "test_session")

        # Verify the result
        assert "response" in result
        assert "GPT response" in result["response"]
        assert "Catalan proverb" in result["response"]
        assert "Spanish translation" in result["response"]
        assert "Traducción" in result["response"]  # Spanish translation label

    @pytest.mark.asyncio
    async def test_process_request_async_error_handling(self, mocker):
        """Test the process_request_async method with error handling."""
        # Mock dependencies to raise an exception
        mocker.patch("app.services.chat_service.track_session", side_effect=Exception("Test error"))

        # Call the method
        result = await ChatService.process_request_async("Hello", "test_session")

        # Verify the result contains the fallback response
        assert "response" in result
        assert "Meow... Something went wrong with my whiskers" in result["response"]

    @pytest.mark.asyncio
    async def test_process_request_async_empty_input(self):
        """Test the process_request_async method with empty input."""
        # Call the method with empty input
        with pytest.raises(ValueError, match="User input cannot be empty"):
            await ChatService.process_request_async("", "test_session")