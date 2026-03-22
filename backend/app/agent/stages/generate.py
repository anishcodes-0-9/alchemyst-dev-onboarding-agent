async def run_generate(session):
    code = "print('Hello from Alchemyst')"

    yield (
        "code",
        {
            "snippet": code,
            "language": "python"
        }
    )

    session["stage"] = "done"

    yield (
        "done",
        {"sessionId": session["id"]}
    )