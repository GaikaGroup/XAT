import os
import logging
import yaml
import time
import random
import asyncio
from typing import Dict, List, Any, Optional
from cachetools import TTLCache

# Configure logging
logger = logging.getLogger(__name__)

# Cache for RAG queries
rag_query_cache = TTLCache(maxsize=200, ttl=1800)  # Cache RAG queries for 30 minutes

# Global variables
RESTAURANT_KEYWORDS_BY_LANG = {}

# RAG configuration
import os
from llama_index.embeddings.openai import OpenAIEmbedding

# Path to the RAG index
RAG_INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rag", "index")
# Embedding model to use
RAG_EMBED_MODEL = OpenAIEmbedding(model="text-embedding-3-small")

# Feature keywords in different languages
FEATURE_KEYWORDS = {
    "has_terrace": {
        "en": ["terrace", "outdoor", "patio"],
        "es": ["terraza", "exterior", "patio"],
        "fr": ["terrasse", "extérieur"],
        "de": ["terrasse", "draußen"],
        "it": ["terrazza", "esterno"],
        "ca": ["terrassa", "exterior"],
        "ru": ["террас", "веранд", "уличн"]
    },
    "sea_view": {
        "en": ["sea view", "ocean view", "water view"],
        "es": ["vista al mar", "vistas al mar", "vista al océano"],
        "fr": ["vue sur la mer", "vue sur l'océan"],
        "de": ["meerblick", "ozeanblick"],
        "it": ["vista mare", "vista sull'oceano"],
        "ca": ["vistes al mar", "vista al mar"],
        "ru": ["вид на море", "морской вид", "вид на океан"]
    },
    "booking": {
        "en": ["book", "reserve", "reservation"],
        "es": ["reservar", "reserva", "reservación"],
        "fr": ["réserver", "réservation"],
        "de": ["buchen", "reservieren", "reservierung"],
        "it": ["prenotare", "prenotazione"],
        "ca": ["reservar", "reserva"],
        "ru": ["бронир", "резервир", "заказ", "забронировать"]
    }
}

# RAG query engine - will be initialized later
rag_query_engine = None

def load_restaurant_keywords(path="app/utils/restaurant_keywords.yaml") -> Dict[str, List[str]]:
    """
    Load restaurant keywords from a YAML file.

    Args:
        path (str): Path to the YAML file containing restaurant keywords

    Returns:
        Dict[str, List[str]]: Dictionary of restaurant keywords by language
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            logger.info("✅ Loaded restaurant keywords from YAML")
            return data.get("keywords", {})
    except Exception as e:
        logger.error(f"❌ Failed to load restaurant keywords: {e}")
        return {}

def query_places(user_query: str, required_features: Dict[str, bool] = None):
    """
    Query the RAG index for places based on user input and required features.

    Args:
        user_query (str): The user's query
        required_features (Dict[str, bool], optional): Dictionary of required features

    Returns:
        List[Dict]: List of places matching the query and required features
    """
    from metrics.inference_metrics import (
        log_latency, log_metric, log_cache_hit, log_cache_miss,
        log_timeout, log_retry, log_connection_pool_usage
    )

    # Import the query engine from rag.query if our local one is None
    global rag_query_engine
    if rag_query_engine is None:
        try:
            from rag.query import rag_query_engine as imported_engine
            if imported_engine is not None:
                logger.info("Using RAG query engine from rag.query module")
                rag_query_engine = imported_engine
        except Exception as e:
            logger.error(f"Failed to import RAG query engine from rag.query: {e}")

    # Enhanced error handling
    if not rag_query_engine:
        logger.error("RAG query engine not initialized, using fallback empty response")
        log_metric("rag_error_count", 1)
        return []

    required_features = required_features or {}

    # Create a cache key that includes both the query and required features
    cache_key = f"{user_query}:{sorted(required_features.items())}"

    # Check if we have a cached result
    if cache_key in rag_query_cache:
        log_cache_hit("rag_query")
        logger.info(f"Using cached RAG results for query: {user_query[:50]}...")
        return rag_query_cache[cache_key]
    else:
        log_cache_miss("rag_query")

    # Implement retry mechanism with exponential backoff
    max_retries = 3
    retry_delay = 1  # seconds
    timeout = 10.0  # 10 seconds timeout for RAG queries

    for retry in range(max_retries):
        try:
            start_time = time.time()

            # Set a timeout for the RAG query
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"RAG query timed out after {timeout} seconds")

            # Set the timeout handler
            original_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))

            try:
                # Log connection pool usage for RAG query engine
                log_connection_pool_usage("rag_query_engine")

                response = rag_query_engine.query(user_query)  # Query the RAG index
                # Reset the alarm
                signal.alarm(0)
            finally:
                # Restore the original handler
                signal.signal(signal.SIGALRM, original_handler)

            elapsed = time.time() - start_time

            # Log RAG latency and result count
            log_latency("rag_query", elapsed)
            log_metric("rag_results_count", len(response.source_nodes))

            # Success - break out of retry loop
            break

        except TimeoutError as e:
            log_timeout("rag")
            logger.error(f"RAG query timeout (attempt {retry+1}/{max_retries}): {e}")

            if retry < max_retries - 1:
                # Wait before retrying with exponential backoff
                wait_time = retry_delay * (2 ** retry)
                logger.info(f"Retrying RAG query in {wait_time} seconds...")
                log_retry("rag")
                time.sleep(wait_time)
            else:
                # All retries failed, return empty results
                logger.error(f"All RAG query retries timed out for: {user_query[:50]}...")
                return []

        except Exception as e:
            log_metric("rag_error_count", 1)
            logger.error(f"RAG query error (attempt {retry+1}/{max_retries}): {e}")

            if retry < max_retries - 1:
                # Wait before retrying with exponential backoff
                wait_time = retry_delay * (2 ** retry)
                logger.info(f"Retrying RAG query in {wait_time} seconds...")
                log_retry("rag")
                time.sleep(wait_time)
            else:
                # All retries failed, return empty results
                logger.error(f"All RAG query retries failed for: {user_query[:50]}...")
                return []

    # Optional: log average similarity if scores are available
    similarities = [
        node.score for node in response.source_nodes
        if hasattr(node, "score") and isinstance(node.score, (float, int))
    ]
    if similarities:
        avg_sim = sum(similarities) / len(similarities)
        log_metric("rag_avg_similarity", avg_sim)

    # DEBUG LOGGING: Show top 7 retrieved docs
    logger.info("🔍 Top retrieved documents for query: %s", user_query)
    for i, node in enumerate(response.source_nodes[:7]):
        logger.info("📄 Result #%d:\n%s\n---", i + 1, node.node.text.strip())

    results = []

    for node in response.source_nodes:
        doc = node.node
        metadata = doc.metadata
        features = metadata.get("features", {})

        if any(features.get(key) != val for key, val in required_features.items()):
            continue

        results.append({
            "name": metadata.get("name", ""),
            "category": metadata.get("category", ""),
            "text": doc.text,
            "direction": metadata.get("direction", ""),
            "has_booking": metadata.get("has_booking", False),
            "email": metadata.get("email", ""),
            "features": features
        })

    # Log filtered count and yield ratio
    log_metric("rag_filtered_count", len(results))
    if response.source_nodes:
        yield_ratio = len(results) / len(response.source_nodes)
        log_metric("rag_filter_yield_ratio", yield_ratio)

    # Store results in cache
    rag_query_cache[cache_key] = results

    return results

def extract_required_features(user_input: str, lang: str = "en") -> dict:
    """
    Extract required features from user input based on detected language.
    Supports multiple languages using the FEATURE_KEYWORDS dictionary.

    Args:
        user_input (str): The user's input text
        lang (str, optional): The detected language code

    Returns:
        dict: Dictionary of required features
    """
    features = {}
    lowered = user_input.lower()

    # Default to English if language not supported
    if lang not in FEATURE_KEYWORDS["has_terrace"]:
        lang = "en"

    # Check for each feature type
    for feature_type, lang_keywords in FEATURE_KEYWORDS.items():
        keywords = lang_keywords.get(lang, lang_keywords.get("en", []))

        # Check if any keyword for this feature is in the user input
        if any(keyword in lowered for keyword in keywords):
            features[feature_type] = True

    return features

def contains_restaurant_trigger(text: str, lang: str = "en") -> bool:
    """
    Check if the text contains restaurant-related keywords in the specified language.

    Args:
        text (str): The text to check
        lang (str, optional): The language code

    Returns:
        bool: True if the text contains restaurant-related keywords, False otherwise
    """
    lowered = text.lower()
    keywords = RESTAURANT_KEYWORDS_BY_LANG.get(lang, [])

    for keyword in keywords:
        if keyword in lowered:
            # Check if this keyword is used in other languages
            used_in_other_langs = any(
                keyword in RESTAURANT_KEYWORDS_BY_LANG.get(other_lang, [])
                for other_lang in RESTAURANT_KEYWORDS_BY_LANG
                if other_lang != lang
            )
            if not used_in_other_langs:
                return True  # Unique word - trigger restaurant dialog
    return False  # No unique keywords found

def create_rag_response(rag_results: List[Dict[str, Any]]) -> str:
    """
    Generate a response in HugDimon's style based on RAG results.

    This function formats the RAG results into a human-readable response,
    including information about each place such as name, description,
    booking availability, contact information, and features.

    Args:
        rag_results (List[Dict[str, Any]]): List of RAG results, where each result
            is a dictionary containing information about a place

    Returns:
        str: Formatted response text with information about each place

    Raises:
        ValueError: If rag_results is None or not a list
    """
    # Validate input
    if rag_results is None:
        logger.error("Received None rag_results")
        raise ValueError("rag_results cannot be None")

    if not isinstance(rag_results, list):
        logger.error(f"rag_results must be a list, got {type(rag_results)}")
        raise ValueError(f"rag_results must be a list, got {type(rag_results)}")

    if not rag_results:
        logger.warning("Empty rag_results, returning empty response")
        return "No places found matching your criteria."
    response_text = ""
    for place in rag_results:
        name = place['name']
        text = place['text']
        has_booking = "Можно забронировать" if place['has_booking'] else "Нет бронирования"
        email = place['email']
        features = place['features']

        # Building response dynamically from RAG results
        response_text += f"\n{name}: {text}\n{has_booking}. Контакт для бронирования: {email}\n"
        if features.get('has_terrace'):
            response_text += "У этого места есть терраса.\n"
        if features.get('sea_view'):
            response_text += "Здесь открывается вид на море.\n"

    return response_text

async def handle_restaurant_dialog(user_input: str, session_id: str = "unknown", lang: str = "en") -> Dict:
    """
    Handle restaurant dialog by calling the restaurant script engine asynchronously.

    Args:
        user_input (str): The user's input text
        session_id (str, optional): The session ID
        lang (str, optional): The language code

    Returns:
        Dict: Response from the restaurant script engine
    """
    try:
        import asyncio
        from restaurant_script_engine import get_next_step

        # Use a timeout for the restaurant script engine
        timeout = 5.0  # 5 seconds timeout

        # Run the potentially blocking operation in a thread pool
        loop = asyncio.get_event_loop()

        # Create a task with timeout
        try:
            # Run the blocking operation in a thread pool with a timeout
            reply = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: get_next_step(session_id, lang, user_input)),
                timeout=timeout
            )
            return {"response": reply}
        except asyncio.TimeoutError:
            logger.error(f"Restaurant script engine timed out after {timeout} seconds")
            log_timeout("restaurant_script")
            return {"response": "Sorry, the restaurant booking system is taking too long to respond. Please try again later! 🐱"}

    except ImportError:
        logger.error("Failed to import restaurant_script_engine")
        return {"response": "Sorry, my restaurant booking system needs maintenance. Try again later! 🐱"}
    except Exception as e:
        logger.error(f"Error with restaurant booking system: {e}")
        return {"response": "My restaurant booking system is currently unavailable. Please try again later! 🐱"}

# Initialize restaurant keywords
RESTAURANT_KEYWORDS_BY_LANG = load_restaurant_keywords("app/utils/restaurant_keywords.yaml")
