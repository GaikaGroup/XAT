import logging
import sys
import os

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import dialog scripts and language detector
from restaurant_booking_script import DIALOG_SCRIPTS
from utils.lang_utils import detect_language

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory store of user sessions
SESSION_STATE = {}

def get_next_step(session_id: str, user_input: str) -> str:
    from utils.lang_utils import detect_language
    from utils.nlp_parser import extract_people_via_gpt, extract_time_via_gpt

    try:
        lang = detect_language(user_input)
    except Exception as e:
        logger.warning(f"Language detection failed, fallback to 'en': {e}")
        lang = "en"

    lang = lang.lower().strip()
    supported_langs = list(DIALOG_SCRIPTS["restaurant_booking"]["steps"][0]["message"].keys())
    if lang not in supported_langs:
        lang = "en"

    script = DIALOG_SCRIPTS["restaurant_booking"]["steps"]

    if session_id not in SESSION_STATE:
        SESSION_STATE[session_id] = {
            "current_step": 0,
            "data": {},
            "dialog": [],
            "lang": lang
        }

    state = SESSION_STATE[session_id]
    step_idx = state["current_step"]
    raw = user_input.strip()
    state["dialog"].append({"user": raw})

    if step_idx > 0:
        prev_step = script[step_idx - 1]
        expected_key = prev_step.get("expect")

        if expected_key == "people":
            parsed = extract_people_via_gpt(raw, lang)
            if parsed != "unknown":
                state["data"]["people"] = parsed
                state["current_step"] += 1
            else:
                return prev_step["message"].get(lang, prev_step["message"]["en"])

        elif expected_key == "time":
            parsed = extract_time_via_gpt(raw, lang)
            if parsed != "unknown":
                state["data"]["time"] = parsed
                state["current_step"] += 1
            else:
                return prev_step["message"].get(lang, prev_step["message"]["en"])

        else:
            state["data"][expected_key] = raw
            state["current_step"] += 1

    # After increment, check if we're done
    if state["current_step"] >= len(script):
        final_responses = {
            "en": "Thanks! Your booking is saved. 🐾",
            "ru": "Спасибо! Ваш заказ принят. 🐾",
            "es": "¡Gracias! Su reserva está hecha. 🐾",
            "fr": "Merci! Votre réservation est faite. 🐾",
            "de": "Danke! Ihre Reservierung ist abgeschlossen. 🐾",
            "ca": "Gràcies! La teva reserva està feta. 🐾"
        }
        final = final_responses.get(lang, final_responses["en"])
        state["dialog"].append({"bot": final})
        return final

    # Get next step message
    step = script[state["current_step"]]
    msg_template = step["message"].get(lang, step["message"]["en"])

    if step["id"] == "confirm":
        try:
            msg_template = msg_template.format(**state["data"])
        except KeyError:
            msg_template = step["message"]["en"]

    state["dialog"].append({"bot": msg_template})
    return msg_template


def get_dialogue_log(session_id: str) -> list:
    return SESSION_STATE.get(session_id, {}).get("dialog", [])

def reset_session(session_id: str) -> bool:
    if session_id in SESSION_STATE:
        SESSION_STATE[session_id] = {
            "current_step": 0,
            "data": {},
            "dialog": []
        }
        logger.info(f"Reset session: {session_id}")
        return True
    return False
