import logging
from langdetect import detect, LangDetectException

# Configure logging
logger = logging.getLogger(__name__)

# List of Russian words that should force Russian language detection
EXCEPTION_WORDS = ["Привет", "Ну", "Че", "Чо", "Емое", "Ёмое", "Йо", "Норм", "Лол", "Ок", "Понял"]

def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    
    This function combines features from both implementations:
    1. Checks for exception words (Russian words) and forces "ru" language if found
    2. Special handling for numeric-only input, returning "same_as_before"
    3. Robust error handling and logging
    
    Args:
        text (str): The text to detect language for
        
    Returns:
        str: ISO 639-1 language code (e.g., "en", "ru", "es")
             or "same_as_before" for numeric-only input
    """
    try:
        if not text.strip():
            logger.warning("Empty input detected, defaulting to English")
            return "en"

        # Check for exception words first (Russian words)
        if any(word.lower() in text.lower() for word in EXCEPTION_WORDS):
            logger.info("Exception word detected, forcing Russian language")
            return "ru"
            
        # Check if input is numeric only
        if text.strip().isdigit():
            logger.info("Input is numeric only → skipping langdetect")
            return "same_as_before"  # Special marker

        # Log the input for debugging
        logger.info(f"User input received: {text}")

        # Use langdetect library for detection
        detected_lang = detect(text)
        logger.debug(f"Detected language: {detected_lang} for text: {text[:50]}...")
        return detected_lang if detected_lang else "en"
    except LangDetectException as e:
        logger.error(f"Error detecting language: {e}")
        return "en"
    except Exception as e:
        logger.error(f"Unexpected error in language detection: {str(e)}")
        return "en"