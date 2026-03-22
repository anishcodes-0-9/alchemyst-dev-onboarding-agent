def match_stack_and_architecture(use_case, features):
    stack = "fastapi"
    architecture = "modular-monolith"

    # 🔹 Use case based decisions
    if use_case == "rag":
        stack = "fastapi"
        architecture = "retrieval-system"

    elif use_case == "agent":
        stack = "fastapi"
        architecture = "agentic-workflow"

    elif use_case == "chatbot":
        stack = "fastapi"
        architecture = "modular-monolith"

    # 🔹 Feature-based overrides
    if "embedding" in features:
        architecture = "retrieval-system"

    if "auth" in features:
        architecture = "service-oriented"

    return {
        "stack": stack,
        "architecture": architecture
    }