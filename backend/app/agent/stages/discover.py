from __future__ import annotations
from app.models.session import SessionState
from app.services.llm import stream_chat
from app.services.alchemyst import alchemyst
from app.agent.prompts import DISCOVER_SYSTEM_PROMPT
from app.agent.extractor import extract_use_case, extract_structured


async def run_discover(session: SessionState):
    # retrieve stored context from previous sessions
    stored_context = await alchemyst.search(session.id, session.history[-1]["content"])

    # build system prompt — inject memory if available
    system = DISCOVER_SYSTEM_PROMPT
    if stored_context:
        memory_block = "\n".join(stored_context)
        system = f"{DISCOVER_SYSTEM_PROMPT}\n\nWhat I already know about this developer:\n{memory_block}"
        session.memory_active = True

    # stream real LLM response
    full_response = ""
    async for token in stream_chat(session.history, system):
        full_response += token
        yield ("token", {"text": token})

    # add assistant response to history
    session.history.append({
        "role": "assistant",
        "content": full_response
    })

    # try structured extraction from [EXTRACTED] block first
    extracted = extract_structured(full_response)

    # fall back to keyword extraction from user message
    last_user_message = session.history[-2]["content"]
    use_case_kw, features_kw = extract_use_case(last_user_message)

    previous_use_case = session.integration.useCase
    existing_features = session.integration.features.copy()

    # use structured if available, else keyword
    use_case = extracted.get("use_case") or use_case_kw
    problem = extracted.get("problem")

    # feature reset on strong override
    if any(word in last_user_message.lower() for word in ["actually", "instead", "make it", "change to"]):
        updated_features = features_kw
    else:
        updated_features = existing_features.copy()
        for f in features_kw:
            if f not in updated_features:
                updated_features.append(f)

    session.integration.useCase = use_case
    session.integration.features = updated_features
    # map user features → product feature (required for codegen)
    if "memory" in updated_features:
        session.integration.feature = "ContextAPI"
    elif "embedding" in updated_features:
        session.integration.feature = "ContextRouter"
    elif "auth" in updated_features:
        session.integration.feature = "IntelliChat"

    # reset derived fields
  # RESET DERIVED FIELDS — only if not no_op
    if not session.integration.no_op:
        session.integration.stack = None
        session.integration.architecture = None

    # advance to match only when LLM outputs [EXTRACTED] block
    # no_op only valid after at least one full cycle (feature must be set)
    has_feature = session.integration.feature is not None
    
    if extracted.get("use_case"):
        session.integration.no_op = False
        session.stage = "match"
    elif has_feature and set(updated_features) == set(existing_features) and use_case == previous_use_case:
        session.integration.no_op = True
        session.stage = "generate"
    else:
        session.integration.no_op = False
        session.stage = "discover"

    # upload newly learned facts to context store
    await alchemyst.upload(session.id, {
        "useCase": session.integration.useCase,
        "features": session.integration.features,
        "problem": problem,
    })

    yield (
        "stage_update",
        {
            "stage": session.stage,
            "integration": session.integration.model_dump(),
            "memoryActive": session.memory_active,
        }
    )