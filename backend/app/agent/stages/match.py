from app.agent.matcher import match_stack_and_architecture


async def run_match(session):
    use_case = session["integration"].get("useCase")
    features = session["integration"].get("features", [])

    result = match_stack_and_architecture(use_case, features)

    # store everything properly
    session["integration"]["stack"] = result["stack"]
    session["integration"]["architecture"] = result["architecture"]
    session["integration"]["feature"] = result["feature"]

    session["stage"] = "generate"

    yield (
        "stage_update",
        {
            "stage": "generate",
            "integration": session["integration"]
        }
    )