import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, List, Tuple, Any, Union

# Configure logging
logger = logging.getLogger(__name__)

# Translation labels for different languages
TRANSLATION_LABELS: Dict[str, str] = {
    "en": "Translation",
    "es": "Traducción",
    "fr": "Traduction",
    "de": "Übersetzung",
    "it": "Traduzione",
    "pt": "Tradução",
    "ru": "Перевод",
    "ca": "Traducció (EN)"
}

# Supported languages
SUPPORTED_LANGS: List[str] = ["en", "es", "fr", "de", "ca", "ru"]

class ChatService:
    @staticmethod
    def get_response(message: str) -> str:
        """
        Get a simple response based on the input message.

        Args:
            message (str): The input message to respond to

        Returns:
            str: A response message based on the input
        """
        responses: Dict[str, str] = {
            "Hola": "¡Hola! ¿Cómo estás?",
            "Adiós": "¡Hasta luego!"
        }
        return responses.get(message, "No entiendo el mensaje.")

    @staticmethod
    def external_api_call(message: str) -> str:
        """
        Simulate an external API call.

        Args:
            message (str): The message to send to the external API

        Returns:
            str: A simulated response from the external API
        """
        return "Simulación de respuesta de API externa"

    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input to prevent potential injection attacks.

        Args:
            text (str): The text to sanitize

        Returns:
            str: The sanitized text

        Raises:
            ValueError: If the input is None or not a string
        """
        # Validate input
        if text is None:
            logger.error("Received None input for sanitization")
            raise ValueError("Input text cannot be None")

        if not isinstance(text, str):
            logger.error(f"Received non-string input for sanitization: {type(text)}")
            raise ValueError(f"Input must be a string, got {type(text)}")

        # Basic sanitization - remove control characters
        sanitized = ''.join(char for char in text if ord(char) >= 32)

        # Limit input length
        if len(sanitized) > 500:
            logger.warning(f"Input truncated from {len(text)} to 500 characters")
            sanitized = sanitized[:500]

        return sanitized

    @staticmethod
    async def process_request_async(user_input: str, session_id: str = "unknown", detected_language: Optional[str] = None) -> Dict[str, str]:
        """
        Process the user request asynchronously with RAG-powered context.

        This function handles the main processing flow for user requests:
        1. Tracks the session
        2. Analyzes sentiment
        3. Detects language (if not provided)
        4. Checks for restaurant triggers
        5. Queries the RAG system for relevant information
        6. Generates a response using ChatGPT
        7. Adds a Catalan proverb based on sentiment
        8. Translates the proverb if necessary

        Args:
            user_input (str): The user's input text
            session_id (str, optional): The session ID for tracking conversations
            detected_language (str, optional): The detected language from transcription service

        Returns:
            Dict[str, str]: Response dictionary with generated text

        Raises:
            ValueError: If user_input is None or empty
            Exception: For various processing errors, which are caught and logged
        """
        # Validate inputs
        if not user_input:
            logger.error("Empty user input received")
            raise ValueError("User input cannot be empty")

        # Sanitize input
        user_input = ChatService.sanitize_input(user_input)
        try:
            from metrics.session_metrics import track_session
            from services.sentiment_service import analyze_sentiment, get_proverb_by_sentiment
            from services.language_service import detect_language
            from services.restaurant_service import contains_restaurant_trigger, handle_restaurant_dialog, extract_required_features, query_places
            from services.chatgpt_service import get_chatgpt_response
            from services.translation_service import translate_text

            track_session(session_id, user_input)
            logger.info(f"📊 Tracked session: {session_id} | message: {user_input[:40]}")

            with ThreadPoolExecutor() as executor:
                sentiment_future = executor.submit(analyze_sentiment, user_input)

                # Use the detected language from transcription service if available
                if detected_language:
                    logger.info(f"Using detected language from transcription service: {detected_language}")
                    detected_lang = detected_language
                else:
                    # Otherwise detect language using our function
                    lang_future = executor.submit(detect_language, user_input)
                    detected_lang = lang_future.result()

                sentiment = sentiment_future.result()

                if detected_lang not in SUPPORTED_LANGS:
                    logger.warning(f"⚠️ Unsupported language detected: {detected_lang}. Falling back to English.")
                    detected_lang = "en"

                # Check for restaurant trigger
                if contains_restaurant_trigger(user_input, detected_lang):
                    logger.info(f"🍽️ Restaurant trigger detected (lang: {detected_lang}) — launching booking dialog")
                    return await handle_restaurant_dialog(user_input, session_id, detected_lang)

                # Extract required features for RAG query
                required_features = extract_required_features(user_input, lang=detected_lang)
                rag_results = query_places(user_input, required_features=required_features)

                # Dynamic context sizing based on result relevance
                max_results = min(len(rag_results), 10)  # Allow up to 10 results if available

                # Sort results by relevance if scores are available
                sorted_results = []
                for i, r in enumerate(rag_results[:max_results]):
                    # Try to get score from source node if available
                    score = 0.0
                    if hasattr(r, 'score'):
                        score = r.get('score', 0.0)
                    # Add position bias - earlier results are likely more relevant
                    position_weight = 1.0 - (i * 0.05)  # Gradually decrease weight
                    final_score = score * position_weight
                    sorted_results.append((r, final_score))

                # Sort by final score, highest first
                sorted_results.sort(key=lambda x: x[1], reverse=True)

                # Build context with the most relevant results
                top_context = "You have the following structured information about places in Cadaqués:\n"
                for r, score in sorted_results:
                    relevance_indicator = "⭐⭐⭐" if score > 0.8 else "⭐⭐" if score > 0.5 else "⭐"
                    top_context += f"""
                Name: {r['name']} {relevance_indicator}
                Category: {r['category']}
                Description: {r['text']}
                Has terrace: {"Yes" if r['features'].get("has_terrace") else "No"}
                Sea view: {"Yes" if r['features'].get("sea_view") else "No"}
                Booking available: {"Yes" if r['has_booking'] else "No"}
                Email: {r['email'] or "Unknown"}
                ---
                """

                # Add a summary of how many places match the criteria
                feature_summary = []
                if required_features.get("has_terrace"):
                    feature_summary.append("with terrace")
                if required_features.get("sea_view"):
                    feature_summary.append("with sea view")
                if required_features.get("booking"):
                    feature_summary.append("with booking available")

                if feature_summary:
                    features_text = ", ".join(feature_summary)
                    top_context += f"\nThere are {len(sorted_results)} places {features_text} in Cadaqués."

                gpt_response = get_chatgpt_response(user_input, detected_lang, context=top_context)

                catalan_proverb, english_translation = get_proverb_by_sentiment(sentiment, user_input)

                # Translate if necessary
                translation_text = english_translation
                if detected_lang not in ["en", "ca"]:
                    translation_text = translate_text(english_translation, detected_lang)

                translation_label = TRANSLATION_LABELS.get(detected_lang, "Translation")

                response_text = f"{gpt_response}\n\n😺 Refrany: {catalan_proverb}"
                if detected_lang == "en":
                    response_text += f"\n🌟 Translation: {english_translation}"
                elif detected_lang == "ca":
                    response_text += f"\n🌟 Traducció (EN): {english_translation}"
                else:
                    response_text += f"\n🌟 {translation_label}: {translation_text}"

                return {"response": response_text}
        except Exception as e:
            logger.error(f"Error in process_request_async: {e}", exc_info=True)
            fallback_response = "Meow... Something went wrong with my whiskers. Try again later! 🐱"
            return {"response": fallback_response}
