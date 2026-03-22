def extract_use_case(message: str):
    msg = message.lower()

    # default
    use_case = "chatbot"
    features = []

    # detect use case
    if any(word in msg for word in ["rag", "document", "search", "retrieval"]):
        use_case = "rag"
    elif any(word in msg for word in ["agent", "workflow", "automation"]):
        use_case = "agent"
    elif any(word in msg for word in ["chat", "chatbot", "gpt", "openai", "ai"]):
        use_case = "chatbot"

    # detect features
    if any(word in msg for word in ["memory", "store", "history"]):
        features.append("memory")

    if any(word in msg for word in ["auth", "authentication", "login"]):
        features.append("auth")

    if any(word in msg for word in ["embedding", "vector", "semantic"]):
        features.append("embedding")

    return use_case, features