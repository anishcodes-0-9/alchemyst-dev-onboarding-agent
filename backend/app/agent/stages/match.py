def route_feature(use_case: str) -> str:
    if not use_case:
        return "IntelliChat"  # fallback

    use_case = use_case.lower()

    if any(k in use_case for k in ["chatbot", "support", "assistant"]):
        return "IntelliChat"

    if any(k in use_case for k in ["gpt", "openai", "replacement"]):
        return "ContextRouter"

    if any(k in use_case for k in ["agent", "workflow", "automation"]):
        return "ContextAPI"

    if any(k in use_case for k in ["rag", "document", "knowledge"]):
        return "ContextAPI"

    return "IntelliChat"  # safe default


async def run_match(session):
    use_case = session["integration"].get("useCase")

    feature = route_feature(use_case)

    session["integration"]["feature"] = feature
    session["stage"] = "generate"

    yield (
        "stage_update",
        {
            "stage": "generate",
            "integration": session["integration"]
        }
    )