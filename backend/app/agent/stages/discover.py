import asyncio
from app.agent.extractor import extract_use_case


async def run_discover(session):
    text = "What are you building?"

    # streaming tokens
    for ch in text:
        yield ("token", {"text": ch})
        await asyncio.sleep(0.01)

    last_message = session["history"][-1]["content"]

    previous_use_case = session["integration"].get("useCase")
    existing_features = session["integration"].get("features", [])

    use_case, extracted_features = extract_use_case(last_message)

#  FIX: do NOT override use_case if message is feature-only
    if extracted_features and len(last_message.strip().split()) <= 3:
        use_case = previous_use_case

    # fallback for vague inputs
    if use_case == "chatbot" and previous_use_case:
        if len(last_message.strip().split()) <= 3:
            use_case = previous_use_case

    #  RESET features if strong override detected
    if any(word in last_message.lower() for word in ["actually", "instead", "make it", "change to"]):
        updated_features = extracted_features
    else:
        updated_features = existing_features.copy()
    for f in extracted_features:
        if f not in updated_features:
            updated_features.append(f)

    #  PROPER NO-OP DETECTION (FIXED)
    if (
        set(updated_features) == set(existing_features)
        and use_case == previous_use_case
    ):
        session["integration"]["no_op"] = True
    else:
        session["integration"]["no_op"] = False

    #  ALWAYS update state (IMPORTANT)
    session["integration"]["useCase"] = use_case
    session["integration"]["features"] = updated_features

    #  RESET DERIVED FIELDS (DO NOT REMOVE)
    session["integration"]["stack"] = None
    session["integration"]["architecture"] = None
    session["integration"]["feature"] = None

    if session["integration"]["no_op"]:
        session["stage"] = "generate"
    else:
        session["stage"] = "match"

    yield (
        "stage_update",
        {
            "stage": session["stage"],
            "integration": session["integration"]
        }
    )