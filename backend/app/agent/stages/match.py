from __future__ import annotations
from app.models.session import SessionState
from app.agent.matcher import match_stack_and_architecture


async def run_match(session: SessionState):
    use_case = session.integration.useCase
    features = session.integration.features

    result = match_stack_and_architecture(use_case, features)

    session.integration.stack = result["stack"]
    session.integration.architecture = result["architecture"]
    session.integration.feature = result["feature"]

    session.stage = "generate"

    yield (
        "stage_update",
        {
            "stage": "generate",
            "integration": session.integration.model_dump()
        }
    )