def match_stack_and_architecture(use_case, features):
    stack = "fastapi"
    architecture = "modular-monolith"
    feature = None

    if use_case == "rag":
        stack = "fastapi"
        architecture = "retrieval-system"
        feature = "ContextAPI"

    elif use_case == "agent":
        stack = "fastapi"
        architecture = "agentic-workflow"
        feature = "ContextAPI"

    elif use_case == "openai_replace":
        stack = "fastapi"
        architecture = "proxy-layer"
        feature = "ContextRouter"

    elif use_case == "chatbot":
        stack = "fastapi"
        architecture = "modular-monolith"
        feature = "IntelliChat"

    if "embedding" in features:
        architecture = "retrieval-system"

    if "auth" in features:
        architecture = "service-oriented"

    return {
        "stack": stack,
        "architecture": architecture,
        "feature": feature
    }