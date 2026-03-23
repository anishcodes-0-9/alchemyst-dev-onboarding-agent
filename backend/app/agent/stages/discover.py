from __future__ import annotations
import asyncio
from app.models.session import SessionState
from app.agent.extractor import extract_use_case


async def run_discover(session: SessionState):
    text = "What are you building?"

    for ch in text:
        yield ("token", {"text": ch})
        await asyncio.sleep(0.01)

    last_message = session.history[-1]["content"]

    previous_use_case = session.integration.useCase
    existing_features = session.integration.features.copy()

    use_case, extracted_features = extract_use_case(last_message)

    # do NOT override use_case if message is feature-only
    if extracted_features and len(last_message.strip().split()) <= 3:
        use_case = previous_use_case

    # fallback for vague inputs
    if use_case == "chatbot" and previous_use_case:
        if len(last_message.strip().split()) <= 3:
            use_case = previous_use_case

    # RESET features if strong override detected
    if any(word in last_message.lower() for word in ["actually", "instead", "make it", "change to"]):
        updated_features = extracted_features
    else:
        updated_features = existing_features.copy()
    for f in extracted_features:
        if f not in updated_features:
            updated_features.append(f)

    # NO-OP DETECTION
    if (
        set(updated_features) == set(existing_features)
        and use_case == previous_use_case
    ):
        session.integration.no_op = True
    else:
        session.integration.no_op = False

    # ALWAYS update state
    session.integration.useCase = use_case
    session.integration.features = updated_features

    # RESET DERIVED FIELDS
    session.integration.stack = None
    session.integration.architecture = None
    session.integration.feature = None

    if session.integration.no_op:
        session.stage = "generate"
    else:
        session.stage = "match"

    yield (
        "stage_update",
        {
            "stage": session.stage,
            "integration": session.integration.model_dump()
        }
    )