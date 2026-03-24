from __future__ import annotations
from app.models.session import SessionState
from app.services.llm import stream_chat
from app.services.alchemyst import alchemyst
from app.agent.prompts import DISCOVER_SYSTEM_PROMPT
from app.agent.extractor import extract_use_case, extract_structured

STACK_KEYWORDS = [
    "python", "javascript", "js", "java", "typescript",
    "node", "fastapi", "flask", "django", "express", "spring"
]

FALLBACK_USE_CASES = {"chatbot"}


async def run_discover(session: SessionState):
    # retrieve stored context from Alchemyst memory
    stored_context = await alchemyst.search(
        session.id,
        session.history[-1]["content"]
    )

    # inject memory into system prompt if available
    system = DISCOVER_SYSTEM_PROMPT
    if stored_context:
        memory_block = "\n".join(stored_context)
        system = (
            f"{DISCOVER_SYSTEM_PROMPT}\n\n"
            f"What I already know about this developer:\n{memory_block}"
        )
        session.memory_active = True

    # stream LLM response token by token
    full_response = ""
    async for token in stream_chat(session.history, system):
        full_response += token
        yield ("token", {"text": token})

    # add assistant turn to history
    session.history.append({
        "role": "assistant",
        "content": full_response
    })

    # primary: structured [EXTRACTED] block from LLM response
    extracted = extract_structured(full_response)

    # fallback: keyword scan of the user's message
    last_user_message = session.history[-2]["content"]
    use_case_kw, features_kw = extract_use_case(last_user_message)

    previous_use_case = session.integration.useCase
    existing_features = session.integration.features.copy()

    # resolve use case — structured takes priority over keyword
    use_case = extracted.get("use_case") or use_case_kw
    problem = extracted.get("problem")

    # accumulate features — reset on strong override signal
    if any(word in last_user_message.lower() for word in ["actually", "instead", "make it", "change to"]):
        updated_features = features_kw
    else:
        updated_features = existing_features.copy()
        for f in features_kw:
            if f not in updated_features:
                updated_features.append(f)

    # never let a fallback default override a previously confirmed specific use case
    if use_case not in FALLBACK_USE_CASES or session.integration.useCase is None:
        session.integration.useCase = use_case
    final_use_case = session.integration.useCase
    session.integration.features = updated_features

    # ── TRANSITION LOGIC ──────────────────────────────────────────────────────

    # path 1: LLM output [EXTRACTED] with all three fields → advance to match
    has_structured = bool(
        extracted.get("use_case")
        and extracted.get("stack")
        and extracted.get("problem")
    )

    # path 2: keyword fallback — use case + stack keyword present in message
    # features are NOT required to advance
    msg_lower = last_user_message.lower()
    has_stack_keyword = any(kw in msg_lower for kw in STACK_KEYWORDS)
    has_keyword = bool(use_case_kw and has_stack_keyword)

    # path 3: no new info and feature already set → no_op, skip to generate
    has_feature = session.integration.feature is not None
    no_new_info = (
        has_feature
        and set(updated_features) == set(existing_features)
        and final_use_case == previous_use_case
    )

    if has_structured or has_keyword:
        # reset derived fields so match always runs fresh
        session.integration.no_op = False
        session.integration.stack = None
        session.integration.architecture = None
        session.integration.feature = None
        session.stage = "match"

    elif no_new_info:
        session.integration.no_op = True
        session.stage = "generate"

    else:
        # still missing info — stay in discover for another round
        session.integration.no_op = False
        session.stage = "discover"

    # upload extracted facts to Alchemyst context store
    await alchemyst.upload(
        session.id,
        {
            "useCase": session.integration.useCase,
            "features": session.integration.features,
            "problem": problem,
        }
    )

    yield (
        "stage_update",
        {
            "stage": session.stage,
            "integration": session.integration.model_dump(),
            "memoryActive": session.memory_active,
        }
    )