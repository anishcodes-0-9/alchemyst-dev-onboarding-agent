import asyncio
from app.agent.extractor import extract_use_case


def extract_features(message: str):
    message = message.lower()
    features = []

    if "memory" in message:
        features.append("memory")

    if "auth" in message or "authentication" in message:
        features.append("auth")

    if "embedding" in message:
        features.append("embedding")

    if "vector" in message:
        features.append("vector_db")

    return features


async def run_discover(session):
    text = "What are you building?"

    # streaming tokens
    for ch in text:
        yield ("token", {"text": ch})
        await asyncio.sleep(0.01)

    #  safe extraction
    last_message = session["history"][-1]["content"]

    previous_use_case = session["integration"].get("useCase")
    existing_features = session["integration"].get("features", [])

    use_case, extracted_features = extract_use_case(last_message)

# fallback for vague inputs
    if use_case == "chatbot" and previous_use_case:
        if len(last_message.strip().split()) <= 3:
            use_case = previous_use_case

#  accumulate features instead of replacing
    updated_features = list(set(existing_features + extracted_features))

    session["integration"]["useCase"] = use_case
    session["integration"]["features"] = updated_features
    session["stage"] = "match"

    yield (
    "stage_update",
    {
        "stage": "match",
        "integration": session["integration"]
    }
)