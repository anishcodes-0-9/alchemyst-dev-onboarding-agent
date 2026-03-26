from __future__ import annotations
import re


# Use cases that require AI/LLM involvement to be valid
AI_USE_CASE_KEYWORDS = {
    "openai_replace": [
        ["replace", "migration", "migrate", "switch", "drop-in", "instead of"],
        ["openai", "gpt-4", "gpt4", "gpt"]
    ],
    "rag": ["rag", "retrieval", "knowledge base", "document search", "semantic search"],
    "agent": ["agent", "autonomous", "workflow automation", "multi-step", "tool use"],
    "chatbot": ["chatbot", "chat interface", "conversational ai", "ai assistant",
                "nlp", "natural language", "llm", "language model"],
}

# These alone do NOT constitute an AI use case
GENERIC_FALLBACK_TRIGGERS = ["chat", "gpt", "openai", "ai", "assistant"]


def extract_use_case(message: str):
    msg = message.lower()
    features = []
    use_case = None

    # Check strong AI use case signals first
    if (
        any(word in msg for word in ["replace", "migration", "migrate", "switch", "drop-in", "instead of"]) and
        any(word in msg for word in ["openai", "gpt-4", "gpt4", "gpt"])
    ):
        use_case = "openai_replace"

    elif any(word in msg for word in ["rag", "retrieval", "knowledge base", "semantic search"]):
        use_case = "rag"

    elif any(word in msg for word in ["agent", "autonomous", "multi-step", "tool use"]):
        use_case = "agent"

    elif any(word in msg for word in [
        "chatbot", "chat interface", "conversational ai", "ai assistant",
        "nlp", "natural language", "language model", "llm"
    ]):
        use_case = "chatbot"

    # Weak signals — only use if explicit AI intent present
    elif any(word in msg for word in GENERIC_FALLBACK_TRIGGERS):
        # Only if there's also an explicit integration/build intent
        if any(word in msg for word in ["integrate", "integration", "add ai", "add chat",
                                         "embed", "connect", "api", "memory", "context"]):
            use_case = "chatbot"

    # Feature detection
    if any(word in msg for word in ["memory", "remember", "history", "context", "session"]):
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