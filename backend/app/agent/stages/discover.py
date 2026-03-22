import asyncio

def extract_use_case(message: str) -> str:
    message = message.lower()

    if "rag" in message or "document" in message:
        return "rag"

    if "chatbot" in message or "chat" in message:
        return "chatbot"

    if "agent" in message or "workflow" in message:
        return "agent"

    return "chatbot"

async def run_discover(session):
    text = "What are you building?"

    for ch in text:
        yield ("token", {"text": ch})
        await asyncio.sleep(0.01)

    # 👇 NEW LINE
    last_message = session["history"][-1]["content"]

    use_case = extract_use_case(last_message)

    session["integration"]["useCase"] = use_case
    session["stage"] = "match"

    yield (
        "stage_update",
        {
            "stage": "match",
            "integration": session["integration"]
        }
    )