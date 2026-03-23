from __future__ import annotations
import re


def extract_use_case(message: str):
    msg = message.lower()

    use_case = "chatbot"
    features = []

    # openai replacement — check FIRST
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

    if any(word in msg for word in ["memory", "store", "history", "remember"]):
        features.append("memory")

    if any(word in msg for word in ["auth", "authentication", "login"]):
        features.append("auth")

    if any(word in msg for word in ["embedding", "vector", "semantic"]):
        features.append("embedding")

    return use_case, features


def extract_structured(llm_response: str) -> dict:
    """
    Parse the [EXTRACTED] block from the LLM discover response.
    Returns dict with use_case, stack, problem keys if found.
    Example: [EXTRACTED] use_case=chatbot stack=python problem=no memory
    """
    match = re.search(r'\[EXTRACTED\]\s*(.+)', llm_response)
    if not match:
        return {}

    result = {}
    raw = match.group(1).strip()

    for pair in re.finditer(r'(\w+)=([^\s]+(?:\s+[^\s=]+)*?)(?=\s+\w+=|$)', raw):
        key = pair.group(1).strip()
        value = pair.group(2).strip()
        result[key] = value

    return result