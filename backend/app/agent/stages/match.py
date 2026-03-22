async def run_match(session):
    use_case = session["integration"].get("useCase")
    features = session["integration"].get("features", [])

    # ✅ INLINE matcher (no external dependency)
    if use_case == "chatbot":
        stack = "fastapi"
        architecture = "modular-monolith"

        if "auth" in features:
            architecture = "service-oriented"

    elif use_case == "rag":
        stack = "fastapi"
        architecture = "retrieval-system"

    else:
        stack = "fastapi"
        architecture = "service-oriented"

    session["integration"]["stack"] = stack

    # 🔒 preserve architecture once set
    if not session["integration"].get("architecture"):
        session["integration"]["architecture"] = architecture

    session["stage"] = "generate"

    yield (
        "stage_update",
        {
            "stage": "generate",
            "integration": session["integration"]
        }
    )