# dialogs/restaurant_dialogue_evaluator.py

def is_booking_complete(session_state: dict) -> bool:
    return session_state.get("current_step", 0) >= 3 and "people" in session_state.get("data", {}) and "time" in session_state.get("data", {})

def summarize_dialog(session_state: dict) -> str:
    data = session_state.get("data", {})
    return f"Booking for {data.get('people')} people at {data.get('time')}."
