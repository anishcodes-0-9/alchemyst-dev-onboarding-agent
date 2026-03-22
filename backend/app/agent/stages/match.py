async def run_match(session):
    # we no longer pick a single feature
    # we rely on features list

    session["stage"] = "generate"

    yield (
        "stage_update",
        {
            "stage": "generate",
            "integration": session["integration"]
        }
    )