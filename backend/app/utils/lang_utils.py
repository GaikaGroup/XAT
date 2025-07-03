# app/utils/lang_utils.py

from langdetect import detect, LangDetectException
import logging

logger = logging.getLogger(__name__)

def detect_language(text: str) -> str:
    try:
        if not text.strip():
            logger.warning("Empty input detected, defaulting to English")
            return "en"

        # ✅ Добавим защиту: если только цифры — используем предыдущий язык
        if text.strip().isdigit():
            logger.info(f"Input is numeric only → skipping langdetect")
            return "same_as_before"  # спец-метка

        lang = detect(text)
        logger.info(f"[LANG-DETECT] '{text[:40]}' → {lang}")
        return lang
    except LangDetectException:
        logger.warning("LangDetectException: fallback to 'en'")
        return "en"
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return "en"
