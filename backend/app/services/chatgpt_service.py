import logging
import time
import os
from typing import Optional
import openai
from cachetools import TTLCache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Load OpenAI API Key
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("Missing OpenAI API Key! Set it in .env or AWS environment variables.")

# Cache for responses
response_cache = TTLCache(maxsize=1000, ttl=3600)  # Cache responses for 1 hour

# Create a global OpenAI client for connection pooling
openai_client = openai.OpenAI(
    api_key=API_KEY,
    timeout=10.0,  # 10 seconds timeout for API calls
    max_retries=3,  # Retry up to 3 times on failures
)

def get_chatgpt_response(user_input: str, detected_lang: str, context: Optional[str] = None) -> str:
    """Generate an AI response using OpenAI GPT with a specific persona and caching."""
    from metrics.inference_metrics import (
        log_cache_hit, log_cache_miss, log_latency, log_metric,
        log_connection_pool_usage, log_retry, log_timeout
    )

    cache_key = f"{user_input}:{detected_lang}"
    if cache_key in response_cache:
        log_cache_hit("gpt")
        logger.info("Returning cached GPT response")
        return response_cache[cache_key]
    else:
        log_cache_miss("gpt")

    # Log connection pool usage
    log_connection_pool_usage("openai")

    try:
        logger.debug(f"Getting ChatGPT response for language: {detected_lang}")
        start_time = time.time()

        # Load persona and utils
        from utils.persona_loader import load_persona_from_file
        from utils.text_utils import user_query_contains_keywords

        base_persona = load_persona_from_file(detected_lang)

        #  Add practical tone for fact-based queries
        factual_keywords = ["address", "how to get", "book", "reservation", "email", "phone"]
        if user_query_contains_keywords(user_input, factual_keywords):
            base_persona += "\n\nRemember: be practical and informative when answering factual questions."

        # Append context from RAG if available
        if context:
            base_persona = f"{context.strip()}\n\n{base_persona.strip()}"

        # Call OpenAI using the global client (connection pooling)
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": base_persona},
                {"role": "user", "content": user_input}
            ],
            max_tokens=300,
            timeout=10.0  # Explicit timeout for this specific request
        )

        gpt_response = response.choices[0].message.content.strip()
        elapsed_time = time.time() - start_time

        # Debug: log usage object from OpenAI
        logger.info(f"OpenAI usage object: {response.usage}")

        # Parse token usage safely
        try:
            usage = response.usage
            total_tokens = int(usage.total_tokens)
            prompt_tokens = int(usage.prompt_tokens)
            completion_tokens = int(usage.completion_tokens)
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse usage tokens: {e}")
            total_tokens = prompt_tokens = completion_tokens = 0

        tokens_per_sec = round(total_tokens / elapsed_time, 2) if elapsed_time > 0 else 0.0

        # Log metrics
        log_latency("gpt", elapsed_time)
        log_metric("gpt_total_tokens", total_tokens)
        log_metric("gpt_prompt_tokens", prompt_tokens)
        log_metric("gpt_completion_tokens", completion_tokens)
        log_metric("gpt_throughput_tps", tokens_per_sec)

        logger.info(
            f"GPT response in {elapsed_time:.2f}s | "
            f"Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}, "
            f"Throughput: {tokens_per_sec} tok/s"
        )

        response_cache[cache_key] = gpt_response
        return gpt_response

    except openai.RateLimitError:
        logger.warning("OpenAI rate limit reached, using fallback response")
        log_metric("openai_rate_limit_errors", 1)
        return translate_text("I'm taking a cat nap. Please try again later.", detected_lang)
    except openai.APITimeoutError:
        logger.warning("OpenAI API timeout, using fallback response")
        log_timeout("openai")
        return translate_text("The internet mouse is too slow right now.", detected_lang)
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        log_metric("openai_api_errors", 1)
        return translate_text("I'm having trouble connecting to my brain. Please try again later.", detected_lang)
    except Exception as e:
        logger.error(f"Error in ChatGPT call: {e}")
        log_metric("openai_unexpected_errors", 1)
        return translate_text("I cannot respond at this moment. 🐾", detected_lang)

# Import the translate_text function from the translation service
from .translation_service import translate_text
