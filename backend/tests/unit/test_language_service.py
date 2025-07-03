import pytest
from unittest.mock import patch
from app.services.language_service import detect_language, EXCEPTION_WORDS

@pytest.mark.unit
class TestLanguageService:
    """Tests for the language_service module."""

    def test_detect_language_english(self):
        """Test detecting English language."""
        text = "Hello, how are you today?"
        result = detect_language(text)
        assert result == "en"

    def test_detect_language_spanish(self):
        """Test detecting Spanish language."""
        text = "Hola, ¿cómo estás hoy?"
        result = detect_language(text)
        assert result == "es"

    def test_detect_language_russian_exception_words(self):
        """Test detecting Russian language using exception words."""
        for word in EXCEPTION_WORDS:
            text = f"Some text with {word} in it"
            result = detect_language(text)
            assert result == "ru", f"Failed for exception word: {word}"

    def test_detect_language_numeric_only(self):
        """Test detecting language with numeric-only input."""
        text = "12345"
        result = detect_language(text)
        assert result == "same_as_before"

    def test_detect_language_empty_input(self):
        """Test detecting language with empty input."""
        text = ""
        result = detect_language(text)
        assert result == "en"

        text = "   "
        result = detect_language(text)
        assert result == "en"

    @patch('app.services.language_service.detect')
    def test_detect_language_langdetect_exception(self, mock_detect):
        """Test handling of LangDetectException."""
        from langdetect import LangDetectException
        # Create a custom exception class that matches the signature
        class CustomLangDetectException(Exception):
            pass
        # Use the custom exception class
        mock_detect.side_effect = CustomLangDetectException("Test exception")

        text = "This should raise an exception"
        result = detect_language(text)
        assert result == "en"
        mock_detect.assert_called_once_with(text)

    @patch('app.services.language_service.detect')
    def test_detect_language_general_exception(self, mock_detect):
        """Test handling of general exceptions."""
        mock_detect.side_effect = Exception("Test exception")

        text = "This should raise an exception"
        result = detect_language(text)
        assert result == "en"
        mock_detect.assert_called_once_with(text)

    @patch('app.services.language_service.detect')
    def test_detect_language_none_result(self, mock_detect):
        """Test handling of None result from langdetect."""
        mock_detect.return_value = None

        text = "This should return None from langdetect"
        result = detect_language(text)
        assert result == "en"
        mock_detect.assert_called_once_with(text)

    def test_detect_language_mixed_case_exception_words(self):
        """Test detecting Russian language using mixed case exception words."""
        for word in EXCEPTION_WORDS:
            # Test with lowercase
            text = f"Some text with {word.lower()} in it"
            result = detect_language(text)
            assert result == "ru", f"Failed for lowercase exception word: {word.lower()}"

            # Test with uppercase
            text = f"Some text with {word.upper()} in it"
            result = detect_language(text)
            assert result == "ru", f"Failed for uppercase exception word: {word.upper()}"
