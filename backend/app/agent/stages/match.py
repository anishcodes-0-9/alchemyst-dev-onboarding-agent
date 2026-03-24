from __future__ import annotations
from app.models.session import SessionState


# deterministic feature routing — matches spec §6.4 exactly
# no LLM call, no matcher.py dependency — pure logic
def resolve_feature(use_case: str | None) -> str | None:
    if use_case == "chatbot":
        return "IntelliChat"
    elif use_case == "openai_replace":
        return "ContextRouter"
    elif use_case in ["rag", "agent"]:
        return "ContextAPI"
    return None


def resolve_stack(use_case: str | None) -> str:
    # all use cases currently use fastapi as the base stack
    return "fastapi"


def resolve_architecture(use_case: str | None, features: list) -> str:
    if use_case == "rag":
        return "retrieval-system"
    elif use_case == "agent":
        return "agentic-workflow"
    elif use_case == "openai_replace":
        return "proxy-layer"
    elif "auth" in features:
        return "service-oriented"
    elif "embedding" in features:
        return "retrieval-system"
    return "modular-monolith"


async def run_match(session: SessionState):
    use_case = session.integration.useCase
    features = session.integration.features

    session.integration.feature = resolve_feature(use_case)
    session.integration.stack = resolve_stack(use_case)
    session.integration.architecture = resolve_architecture(use_case, features)

    session.stage = "generate"

    yield (
        "stage_update",
        {
            "stage": "generate",
            "integration": session.integration.model_dump()
        }
    )