import pytest
import time
from unittest.mock import patch

@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmarks for critical paths in the application."""

    @pytest.mark.benchmark(
        group="services",
        min_time=0.1,
        max_time=0.5,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_chat_service_sanitize_input(self, benchmark):
        """Benchmark the ChatService.sanitize_input method."""
        from app.services.chat_service import ChatService

        # Create a long input string
        input_text = "x" * 1000

        # Benchmark the function
        result = benchmark(ChatService.sanitize_input, input_text)

        # Verify the result
        assert len(result) == 500
        assert result == "x" * 500

    @pytest.mark.benchmark(
        group="services",
        min_time=0.1,
        max_time=0.5,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_translation_service_cached(self, benchmark, mock_translator):
        """Benchmark the translate_text function with cached results."""
        from app.services.translation_service import translate_text, translation_cache

        # Clear the cache
        translation_cache.clear()

        # Call the function once to cache the result
        translate_text("Hello, world!", "es")

        # Benchmark the function with cached result
        result = benchmark(translate_text, "Hello, world!", "es")

        # Verify the result
        assert result == "Mocked translation"

    @pytest.mark.benchmark(
        group="services",
        min_time=0.1,
        max_time=0.5,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_translation_service_uncached(self, benchmark, mock_translator):
        """Benchmark the translate_text function with uncached results."""
        from app.services.translation_service import translate_text, translation_cache

        # Clear the cache
        translation_cache.clear()

        # Generate unique inputs for each benchmark run
        def translate_with_unique_input():
            # Use time to create a unique input
            unique_input = f"Hello, world! {time.time()}"
            return translate_text(unique_input, "es")

        # Benchmark the function with uncached result
        result = benchmark(translate_with_unique_input)

        # Verify the result
        assert result == "Mocked translation"

    @pytest.mark.benchmark(
        group="services",
        min_time=0.1,
        max_time=0.5,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_chatgpt_service_cached(self, benchmark, mock_openai):
        """Benchmark the get_chatgpt_response function with cached results."""
        from app.services.chatgpt_service import get_chatgpt_response, response_cache

        # Clear the cache
        response_cache.clear()

        # Call the function once to cache the result
        get_chatgpt_response("Hello, world!", "en")

        # Benchmark the function with cached result
        result = benchmark(get_chatgpt_response, "Hello, world!", "en")

        # Verify the result
        assert result == "Mocked OpenAI response"

    @pytest.mark.benchmark(
        group="services",
        min_time=0.1,
        max_time=0.5,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_chatgpt_service_uncached(self, benchmark, mock_openai):
        """Benchmark the get_chatgpt_response function with uncached results."""
        from app.services.chatgpt_service import get_chatgpt_response, response_cache

        # Clear the cache
        response_cache.clear()

        # Generate unique inputs for each benchmark run
        def chatgpt_with_unique_input():
            # Use time to create a unique input
            unique_input = f"Hello, world! {time.time()}"
            return get_chatgpt_response(unique_input, "en")

        # Benchmark the function with uncached result
        result = benchmark(chatgpt_with_unique_input)

        # Verify the result
        assert result == "Mocked OpenAI response"

    @pytest.mark.benchmark(
        group="api",
        min_time=0.1,
        max_time=1.0,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_chat_endpoint_performance(self, benchmark, client, mock_openai, mock_sentiment_analyzer, mock_language_detector):
        """Benchmark the chat endpoint."""
        # Prepare the request data
        data = {
            "message": "Hello, world!",
            "session_id": "test_session"
        }

        # Define a function to call the endpoint
        def call_chat_endpoint():
            return client.post("/chat", json=data)

        # Benchmark the endpoint
        response = benchmark(call_chat_endpoint)

        # Verify the response
        assert response.status_code == 200
        assert "response" in response.json

    @pytest.mark.benchmark(
        group="api",
        min_time=0.1,
        max_time=1.0,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_guide_endpoint_performance(self, benchmark, client, mock_openai, mock_rag_query_engine):
        """Benchmark the guide endpoint."""
        # Prepare the request data
        data = {
            "message": "Tell me about restaurants in Cadaqués"
        }

        # Define a function to call the endpoint
        def call_guide_endpoint():
            return client.post("/guide", json=data)

        # Benchmark the endpoint
        response = benchmark(call_guide_endpoint)

        # Verify the response
        assert response.status_code == 200
        assert "response" in response.json

    @pytest.mark.benchmark(
        group="services",
        min_time=0.1,
        max_time=0.5,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_language_detection(self, benchmark, mock_language_detector):
        """Benchmark the detect_language function."""
        from app.services.language_service import detect_language

        # Prepare test inputs with different characteristics
        inputs = [
            "Hello, how are you today?",  # English
            "Hola, ¿cómo estás hoy?",     # Spanish
            "Привет, как дела сегодня?",   # Russian with exception words
            "12345",                      # Numeric only
            ""                            # Empty
        ]

        # Benchmark the function with multiple inputs
        def detect_languages():
            results = []
            for text in inputs:
                results.append(detect_language(text))
            return results

        # Run the benchmark
        results = benchmark(detect_languages)

        # Verify we got results for all inputs
        assert len(results) == len(inputs)

    @pytest.mark.benchmark(
        group="services",
        min_time=0.1,
        max_time=0.5,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_sentiment_analysis(self, benchmark, mock_sentiment_analyzer):
        """Benchmark the analyze_sentiment function."""
        from app.services.sentiment_service import analyze_sentiment

        # Prepare test inputs with different sentiments
        inputs = [
            "I love this product, it's amazing!",  # Positive
            "I hate this product, it's terrible!", # Negative
            "This is a product."                   # Neutral
        ]

        # Benchmark the function with multiple inputs
        def analyze_sentiments():
            results = []
            for text in inputs:
                results.append(analyze_sentiment(text))
            return results

        # Run the benchmark
        results = benchmark(analyze_sentiments)

        # Verify we got results for all inputs
        assert len(results) == len(inputs)

    @pytest.mark.benchmark(
        group="services",
        min_time=0.1,
        max_time=1.0,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_restaurant_query_cached(self, benchmark, mock_rag_query_engine):
        """Benchmark the query_places function with cached results."""
        from app.services.restaurant_service import query_places, rag_query_cache

        # Clear the cache
        rag_query_cache.clear()

        # Call the function once to cache the result
        query_places("restaurants with sea view")

        # Benchmark the function with cached result
        result = benchmark(query_places, "restaurants with sea view")

        # Verify the result
        assert isinstance(result, list)

    @pytest.mark.benchmark(
        group="api",
        min_time=0.1,
        max_time=1.0,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_health_endpoint_performance(self, benchmark, client):
        """Benchmark the health endpoint."""
        # Define a function to call the endpoint
        def call_health_endpoint():
            return client.get("/health")

        # Benchmark the endpoint
        response = benchmark(call_health_endpoint)

        # Verify the response
        assert response.status_code == 200
        assert "status" in response.json

    @pytest.mark.benchmark(
        group="api",
        min_time=0.1,
        max_time=1.0,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_metrics_endpoint_performance(self, benchmark, client):
        """Benchmark the metrics endpoint."""
        # Define a function to call the endpoint
        def call_metrics_endpoint():
            return client.get("/metrics")

        # Benchmark the endpoint
        response = benchmark(call_metrics_endpoint)

        # Verify the response
        assert response.status_code == 200
