def extract_use_case(message: str):
    msg = message.lower()

    use_case = "chatbot"
    features = []

    # openai replacement check FIRST — before generic ai/chatbot check
    if (
        any(word in msg for word in ["replace", "migration", "migrate", "switch", "drop-in", "instead of"]) and
        any(word in msg for word in ["openai", "gpt-4", "gpt4", "gpt"])
    ):
        use_case = "openai_replace"

    elif any(word in msg for word in ["rag", "document", "search", "retrieval", "knowledge base"]):
        use_case = "rag"

    elif any(word in msg for word in ["agent", "workflow", "automation", "autonomous"]):
        use_case = "agent"

    elif any(word in msg for word in ["chat", "chatbot", "gpt", "openai", "ai", "assistant"]):
        use_case = "chatbot"

    # feature detection
    if any(word in msg for word in ["memory", "store", "history", "remember"]):
        features.append("memory")

    if any(word in msg for word in ["auth", "authentication", "login"]):
        features.append("auth")

    if any(word in msg for word in ["embedding", "vector", "semantic"]):
        features.append("embedding")

    return use_case, features