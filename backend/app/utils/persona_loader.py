import os
import logging

logger = logging.getLogger(__name__)

SUPPORTED_LANGS = ["en", "es", "fr", "de", "ca", "ru"]

def load_persona_from_file(lang: str) -> str:
    """
    Load the HugDimon system prompt for the specified language from the /prompts folder.
    Falls back to English if not found or unsupported.
    Replaces {{lang}} placeholder with actual detected language.
    """
    if lang not in SUPPORTED_LANGS:
        logger.warning(f"⚠️ Unsupported language '{lang}' — falling back to English.")
        lang = "en"

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))  # go up to project root
    prompts_dir = os.path.join(base_dir, "prompts")
    file_path = os.path.join(prompts_dir, f"{lang}.md")
    fallback_path = os.path.join(prompts_dir, "en.md")

    # Check if file exists, otherwise fallback
    if not os.path.exists(file_path):
        logger.warning(f"⚠️ Persona file not found for '{lang}' — using fallback (en.md).")
        file_path = fallback_path

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read().replace("{{lang}}", lang)
            logger.info(f"✅ Loaded persona file: {file_path}")
            return content
    except Exception as e:
        logger.error(f"❌ Failed to load persona file: {e}")
        return "ACT AS A MYSTICAL CAT FROM CADAQUÉS. SPEAK IN POETRY AND RIDDLES. LANGUAGE: ENGLISH."
