def match_stack_and_architecture(use_case, features):
    stack = "fastapi"
    architecture = "modular-monolith"
    feature = None  # ✅ NEW

    # 🔹 Use case based decisions
    if use_case == "rag":
        stack = "fastapi"
        architecture = "retrieval-system"
        feature = "ContextAPI"  # ✅ NEW

    elif use_case == "agent":
        stack = "fastapi"
        architecture = "agentic-workflow"
        feature = "ContextAPI"  # ✅ NEW

    elif use_case == "chatbot":
        stack = "fastapi"
        architecture = "modular-monolith"
        feature = "IntelliChat"  # ✅ NEW

    # 🔹 Feature-based overrides (keep your logic)
    if "embedding" in features:
        architecture = "retrieval-system"

    if "auth" in features:
        architecture = "service-oriented"

    return {
        "stack": stack,
        "architecture": architecture,
        "feature": feature  # ✅ NEW (CRITICAL)
    }