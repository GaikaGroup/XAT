import logging
from app.main import get_chatgpt_response

logger = logging.getLogger(__name__)

def extract_time_via_gpt(user_input: str, lang: str = "en") -> str:
    """
    Uses ChatGPT to extract time from the user's input in a restaurant reservation context.
    Returns the time as a string (e.g., "19:00", "7pm") or 'unknown' if unclear.
    """
    prompt = f"""
We are in a restaurant booking scenario.

The assistant asked: "What time would you like the reservation?"

The user replied: "{user_input}"

Please extract the time from the user's response, in a simple format like "19:00" or "7pm".
If the time is unclear or missing, return "unknown".
Only return the time value, no extra explanation.
"""

    try:
        response = get_chatgpt_response(prompt, lang).strip()
        logger.info(f"[GPT time extraction] Input: '{user_input}' → GPT returned: '{response}'")

        # Basic check for time-like string (very relaxed)
        if any(char.isdigit() for char in response):
            return response
        return "unknown"
    except Exception as e:
        logger.error(f"Failed to extract time via GPT: {e}")
        return "unknown"
