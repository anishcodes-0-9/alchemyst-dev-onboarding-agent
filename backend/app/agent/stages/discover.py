import asyncio
from app.agent.extractor import extract_use_case


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
    updated_features = existing_features.copy()

    for f in extracted_features:
        if f not in updated_features:
            updated_features.append(f)

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