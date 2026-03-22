async def run_match(session):
    session["integration"]["feature"] = "IntelliChat"
    session["stage"] = "generate"

    yield (
        "stage_update",
        {
            "stage": "generate",
            "integration": session["integration"]
        }
    )