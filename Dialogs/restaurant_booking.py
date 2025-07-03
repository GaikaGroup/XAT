# dialogs/restaurant_booking.py

from dialogs.restaurant_script_engine import get_next_step

async def handle_restaurant_dialog(user_input: str, session_id: str = "unknown", lang: str = "en") -> dict:
    reply = get_next_step(session_id, lang, user_input)
    return {"response": reply}

