import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from flask.testing import FlaskClient

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Add the app directory to the Python path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app"))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Import the app factory
from backend.app.app_factory import create_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create the Flask app with testing config
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DEBUG": False,
    })

    # Return the app for testing
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

# Mock fixtures for external services
@pytest.fixture
def mock_openai():
    """Mock the OpenAI API client."""
    with patch("openai.OpenAI") as mock:
        # Configure the mock to return a predictable response
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="Mocked OpenAI response"))]
        mock_client.chat.completions.create.return_value = mock_completion
        mock.return_value = mock_client
        yield mock

@pytest.fixture
def mock_translator():
    """Mock the GoogleTranslator."""
    with patch("deep_translator.GoogleTranslator") as mock:
        # Configure the mock to return a predictable response
        mock_translator = MagicMock()
        mock_translator.translate.return_value = "Mocked translation"
        mock.return_value = mock_translator
        yield mock

@pytest.fixture
def mock_rag_query_engine():
    """Mock the RAG query engine."""
    with patch("backend.app.services.restaurant_service.rag_query_engine") as mock:
        # Configure the mock to return a predictable response
        mock_response = MagicMock()
        mock_node = MagicMock()
        mock_node.node.text = "Mocked RAG text"
        mock_node.node.metadata = {
            "name": "Mocked Restaurant",
            "category": "Mocked Category",
            "direction": "Mocked Direction",
            "has_booking": True,
            "email": "mock@example.com",
            "features": {
                "has_terrace": True,
                "sea_view": True
            }
        }
        mock_response.source_nodes = [mock_node]
        mock.query.return_value = mock_response
        yield mock

@pytest.fixture
def mock_sentiment_analyzer():
    """Mock the sentiment analyzer."""
    with patch("textblob.TextBlob") as mock:
        # Configure the mock to return a predictable response
        mock_blob = MagicMock()
        mock_blob.sentiment.polarity = 0.5  # Positive sentiment
        mock.return_value = mock_blob
        yield mock

@pytest.fixture
def mock_language_detector():
    """Mock the language detector."""
    with patch("langdetect.detect") as mock:
        # Configure the mock to return a predictable response
        mock.return_value = "en"
        yield mock
