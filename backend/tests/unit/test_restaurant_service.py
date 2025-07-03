import pytest
from unittest.mock import patch, MagicMock
import asyncio

from app.services.restaurant_service import (
    extract_required_features,
    contains_restaurant_trigger,
    create_rag_response,
    load_restaurant_keywords,
    handle_restaurant_dialog
)

@pytest.mark.unit
class TestRestaurantService:
    """Tests for the restaurant_service module."""

    @patch('app.services.restaurant_service.FEATURE_KEYWORDS')
    def test_extract_required_features(self, mock_feature_keywords):
        """Test extracting required features from user input."""
        # Setup mock feature keywords
        mock_feature_keywords.__getitem__.return_value = {
            "en": ["terrace", "outdoor"],
            "es": ["terraza", "exterior"]
        }
        mock_feature_keywords.items.return_value = [
            ("has_terrace", {
                "en": ["terrace", "outdoor"],
                "es": ["terraza", "exterior"]
            }),
            ("sea_view", {
                "en": ["sea view", "ocean view"],
                "es": ["vista al mar", "vista al océano"]
            })
        ]

        # Test with English input
        user_input = "I want a restaurant with a terrace"
        result = extract_required_features(user_input, "en")
        assert "has_terrace" in result
        assert result["has_terrace"] is True

        # Test with Spanish input
        user_input = "Quiero un restaurante con terraza"
        result = extract_required_features(user_input, "es")
        assert "has_terrace" in result
        assert result["has_terrace"] is True

        # Test with no matching features
        user_input = "I want a restaurant"
        result = extract_required_features(user_input, "en")
        assert result == {}

        # Test with unsupported language
        user_input = "Je veux un restaurant avec terrasse"
        result = extract_required_features(user_input, "fr")
        assert result == {}

    @patch('app.services.restaurant_service.RESTAURANT_KEYWORDS_BY_LANG')
    def test_contains_restaurant_trigger(self, mock_keywords):
        """Test checking if text contains restaurant-related triggers."""
        # Setup mock keywords
        mock_keywords.get.side_effect = lambda lang, default=None: {
            "en": ["restaurant", "cafe", "dining"],
            "es": ["restaurante", "cafetería", "comida"]
        }.get(lang, [])
        mock_keywords.__iter__.return_value = ["en", "es"]

        # Test with English input containing trigger
        text = "I want to find a restaurant"
        assert contains_restaurant_trigger(text, "en") is True

        # Test with Spanish input containing trigger
        text = "Quiero encontrar un restaurante"
        assert contains_restaurant_trigger(text, "es") is True

        # Test with input not containing trigger
        text = "I want to go to the beach"
        assert contains_restaurant_trigger(text, "en") is False

        # Test with input containing trigger used in multiple languages
        # Mock the behavior where "cafe" is used in both English and Spanish
        mock_keywords.get.side_effect = lambda lang, default=None: {
            "en": ["restaurant", "cafe", "dining"],
            "es": ["restaurante", "cafe", "comida"]
        }.get(lang, [])

        text = "I want to go to a cafe"
        assert contains_restaurant_trigger(text, "en") is False  # Should be False because "cafe" is used in multiple languages

    def test_create_rag_response(self):
        """Test creating a response based on RAG results."""
        # Test with valid RAG results
        rag_results = [
            {
                "name": "Test Restaurant",
                "text": "A nice restaurant",
                "has_booking": True,
                "email": "test@example.com",
                "features": {"has_terrace": True, "sea_view": False}
            },
            {
                "name": "Another Restaurant",
                "text": "Another nice restaurant",
                "has_booking": False,
                "email": "another@example.com",
                "features": {"has_terrace": False, "sea_view": True}
            }
        ]

        response = create_rag_response(rag_results)
        assert "Test Restaurant" in response
        assert "A nice restaurant" in response
        assert "Можно забронировать" in response
        assert "test@example.com" in response
        assert "У этого места есть терраса" in response
        assert "Another Restaurant" in response
        assert "Another nice restaurant" in response
        assert "Нет бронирования" in response
        assert "another@example.com" in response
        assert "Здесь открывается вид на море" in response

        # Test with empty RAG results
        response = create_rag_response([])
        assert response == "No places found matching your criteria."

        # Test with None RAG results
        with pytest.raises(ValueError, match="rag_results cannot be None"):
            create_rag_response(None)

        # Test with non-list RAG results
        with pytest.raises(ValueError, match="rag_results must be a list"):
            create_rag_response("not a list")

    @patch('app.services.restaurant_service.yaml')
    @patch('app.services.restaurant_service.open')
    def test_load_restaurant_keywords(self, mock_open, mock_yaml):
        """Test loading restaurant keywords from a YAML file."""
        # Setup mock yaml.safe_load to return a dictionary
        mock_yaml.safe_load.return_value = {"keywords": {"en": ["restaurant", "cafe"]}}

        # Test successful loading
        result = load_restaurant_keywords()
        assert result == {"en": ["restaurant", "cafe"]}
        mock_open.assert_called_once()
        mock_yaml.safe_load.assert_called_once()

        # Test exception handling
        mock_open.side_effect = Exception("Test exception")
        result = load_restaurant_keywords()
        assert result == {}

    @pytest.mark.asyncio
    @patch('app.services.restaurant_service.get_next_step')
    async def test_handle_restaurant_dialog(self, mock_get_next_step):
        """Test handling restaurant dialog."""
        # Setup mock get_next_step
        mock_get_next_step.return_value = "Restaurant response"

        # Test successful handling
        result = await handle_restaurant_dialog("I want to book a restaurant", "test_session", "en")
        assert result == {"response": "Restaurant response"}
        mock_get_next_step.assert_called_once_with("test_session", "en", "I want to book a restaurant")

        # Test timeout
        mock_get_next_step.side_effect = asyncio.TimeoutError("Test timeout")
        result = await handle_restaurant_dialog("I want to book a restaurant", "test_session", "en")
        assert "Sorry, the restaurant booking system is taking too long to respond" in result["response"]

        # Test import error
        with patch('app.services.restaurant_service.asyncio.wait_for', side_effect=ImportError("Test import error")):
            result = await handle_restaurant_dialog("I want to book a restaurant", "test_session", "en")
            assert "Sorry, my restaurant booking system needs maintenance" in result["response"]

    @patch('app.services.restaurant_service.rag_query_engine')
    @patch('app.services.restaurant_service.rag_query_cache')
    def test_query_places_cache_hit(self, mock_cache, mock_engine):
        """Test querying places with cache hit."""
        # This test requires more complex mocking and is left as a placeholder
        # A full implementation would require mocking the signal module, the rag_query_engine,
        # the rag_query_cache, and the metrics.inference_metrics module
        pass
