import asyncio


async def run_discover(session):
    text = "What are you building?"

    for ch in text:
        yield ("token", {"text": ch})
        await asyncio.sleep(0.01)

    session["integration"]["useCase"] = "chatbot"
    session["stage"] = "match"

    yield (
        "stage_update",
        {
            "stage": "match",
            "integration": session["integration"]
        }
    )