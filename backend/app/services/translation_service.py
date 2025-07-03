import logging
import time
from deep_translator import GoogleTranslator
from cachetools import TTLCache
from typing import Dict

# Configure logging
logger = logging.getLogger(__name__)

# Cache for translations
translation_cache = TTLCache(maxsize=500, ttl=86400)  # Cache translations for 1 day

# Create a pool of translators for different language pairs
# This avoids creating a new translator for each request
translator_pool: Dict[str, GoogleTranslator] = {}

def translate_text(text: str, target_language: str) -> str:
    """Translate text to the target language using GoogleTranslator with caching."""
    if not text or target_language == "en":
        return text  # No translation needed

    from metrics.inference_metrics import (
        log_cache_hit, log_cache_miss, log_latency, log_metric,
        log_connection_pool_usage, log_timeout
    )

    cache_key = f"{text}:{target_language}"
    if cache_key in translation_cache:
        log_cache_hit("translation")
        logger.debug(f"Using cached translation for: {text[:30]}...")
        return translation_cache[cache_key]
    else:
        log_cache_miss("translation")

    # Log connection pool usage when using a translator from the pool
    pool_key = f"en-{target_language}"
    if pool_key in translator_pool:
        log_connection_pool_usage(f"translator_{pool_key}")

    try:
        # Get translator from pool or create a new one
        pool_key = f"en-{target_language}"
        if pool_key not in translator_pool:
            logger.debug(f"Creating new translator for {pool_key}")
            translator_pool[pool_key] = GoogleTranslator(source='en', target=target_language)

        translator = translator_pool[pool_key]

        # Add timeout handling
        start_time = time.time()
        max_time = 5.0  # 5 seconds timeout

        # Translate with timeout handling
        try:
            translated_text = translator.translate(text)
            elapsed = time.time() - start_time

            # Log translation time
            logger.debug(f"Translation took {elapsed:.2f}s")

            # Cache the result
            translation_cache[cache_key] = translated_text
            logger.debug(f"Translated '{text[:30]}...' to {target_language}")
            return translated_text
        except Exception as e:
            elapsed = time.time() - start_time
            if elapsed >= max_time:
                logger.error(f"Translation timed out after {elapsed:.2f}s")
                raise TimeoutError(f"Translation timed out after {elapsed:.2f}s") from e
            raise
    except ConnectionError as e:
        logger.error(f"Translation service connection error: {e}")
        log_metric("translation_connection_errors", 1)
        return text
    except TimeoutError as e:
        logger.error(f"Translation service timeout: {e}")
        log_timeout("translation")
        return text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        log_metric("translation_unexpected_errors", 1)
        return text
