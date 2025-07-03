import pytest
from unittest.mock import MagicMock, patch

from app.services.translation_service import translate_text, translation_cache, translator_pool

class TestTranslationService:
    """Tests for the Translation service."""

    def test_translate_text_basic(self, mock_translator):
        """Test the translate_text function with basic functionality."""
        # Call the function
        response = translate_text("Hello", "es")

        # Verify the response
        assert response == "Mocked translation"
        
        # Verify the translator was called correctly
        mock_translator.assert_called_once()
        
        # Verify the translator was initialized with the correct parameters
        call_args = mock_translator.call_args[1]
        assert call_args["source"] == "en"
        assert call_args["target"] == "es"

    def test_translate_text_no_translation_needed(self, mock_translator):
        """Test that no translation is performed when not needed."""
        # Test with empty text
        response = translate_text("", "es")
        assert response == ""
        mock_translator.assert_not_called()
        
        # Test with English target language
        response = translate_text("Hello", "en")
        assert response == "Hello"
        mock_translator.assert_not_called()

    def test_translate_text_caching(self, mock_translator):
        """Test that translations are cached."""
        # Clear the cache
        translation_cache.clear()
        
        # Call the function twice with the same input
        response1 = translate_text("Hello", "es")
        response2 = translate_text("Hello", "es")
        
        # Verify both responses are the same
        assert response1 == response2
        
        # Verify the translator was called only once
        assert mock_translator.call_count == 1

    def test_translate_text_different_languages(self, mock_translator):
        """Test that different languages use different cache keys."""
        # Clear the cache
        translation_cache.clear()
        
        # Call the function with different target languages
        translate_text("Hello", "es")
        translate_text("Hello", "fr")
        
        # Verify the translator was called twice
        assert mock_translator.call_count == 2
        
        # Verify the translator was initialized with different target languages
        call_args_list = mock_translator.call_args_list
        assert call_args_list[0][1]["target"] == "es"
        assert call_args_list[1][1]["target"] == "fr"

    def test_translate_text_translator_pool(self, mock_translator):
        """Test that the translator pool is used."""
        # Clear the pool
        translator_pool.clear()
        
        # Call the function
        translate_text("Hello", "es")
        
        # Verify the translator was added to the pool
        assert "en-es" in translator_pool
        
        # Call the function again with the same language
        translate_text("Different text", "es")
        
        # Verify the translator was called only once (for initialization)
        assert mock_translator.call_count == 1

    def test_translate_text_connection_error(self, mock_translator):
        """Test handling of connection errors."""
        # Configure the mock to raise a connection error
        mock_instance = MagicMock()
        mock_instance.translate.side_effect = ConnectionError("Connection error")
        mock_translator.return_value = mock_instance
        
        # Call the function
        response = translate_text("Hello", "es")
        
        # Verify the original text is returned
        assert response == "Hello"

    def test_translate_text_timeout_error(self, mock_translator):
        """Test handling of timeout errors."""
        # Configure the mock to raise a timeout error
        mock_instance = MagicMock()
        mock_instance.translate.side_effect = TimeoutError("Timeout error")
        mock_translator.return_value = mock_instance
        
        # Call the function
        response = translate_text("Hello", "es")
        
        # Verify the original text is returned
        assert response == "Hello"

    def test_translate_text_general_error(self, mock_translator):
        """Test handling of general errors."""
        # Configure the mock to raise a general error
        mock_instance = MagicMock()
        mock_instance.translate.side_effect = Exception("General error")
        mock_translator.return_value = mock_instance
        
        # Call the function
        response = translate_text("Hello", "es")
        
        # Verify the original text is returned
        assert response == "Hello"

    @patch("app.services.translation_service.log_metric")
    def test_translate_text_metrics(self, mock_log_metric, mock_translator):
        """Test that metrics are logged."""
        # Clear the cache
        translation_cache.clear()
        
        # Call the function
        translate_text("Hello", "es")
        
        # Verify metrics were logged
        assert mock_log_metric.call_count > 0