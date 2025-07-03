def user_query_contains_keywords(user_input: str, keywords: list[str]) -> bool:
    """Check if user input contains any of the specified keywords (case insensitive)."""
    lowered = user_input.lower()
    return any(keyword.lower() in lowered for keyword in keywords)
