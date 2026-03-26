from __future__ import annotations
from app.models.session import SessionState


def resolve_feature(use_case: str | None) -> str | None:
    if use_case == "chatbot":
        return "OpenAI Chat API"
    elif use_case in ["rag", "agent"]:
        return "OpenAI + Retrieval"
    elif use_case == "backend":
        return "standard API"
    elif use_case == "openai_replace":
        return "OpenAI Compatible API"
    return "standard API"


def resolve_stack(language: str | None, use_case: str | None) -> str:
    lang = (language or "python").lower()

    if lang == "python":
        return "python / fastapi"
    elif lang == "javascript":
        return "node / express"
    elif lang == "java":
        return "java / spring boot"

    return lang


def resolve_architecture(use_case: str | None, features: list) -> str:
    if use_case == "rag":
        return "retrieval-augmented"
    elif use_case == "agent":
        return "tool-augmented"
    elif use_case == "openai_replace":
        return "api-compatible-layer"

    return "stateless-service"


async def run_match(session: SessionState):
    use_case = session.integration.useCase
    features = session.integration.features

    session.integration.feature = None
    session.integration.stack = None
    session.integration.architecture = None

    session.stage = "generate"

    yield (
        "stage_update",
        {
            "stage": "generate",
            "integration": session.integration.model_dump()
        }
    )