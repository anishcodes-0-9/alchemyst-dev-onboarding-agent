from __future__ import annotations
from app.models.session import SessionState
from app.services.llm import stream_chat
from app.services.context_store import context_store
from app.agent.prompts import DISCOVER_SYSTEM_PROMPT
from app.agent.extractor import extract_use_case, extract_structured

STACK_KEYWORDS = [
    "python", "javascript", "js", "java", "typescript",
    "node", "fastapi", "flask", "django", "express", "spring"
]

FALLBACK_USE_CASES = {"chatbot"}


def _detect_language(text: str) -> str | None:
    t = text.lower()
    if any(kw in t for kw in ["javascript", "js", "node", "express", "typescript"]):
        return "javascript"
    if any(kw in t for kw in ["java", "spring"]):
        return "java"
    if any(kw in t for kw in ["python", "fastapi", "flask", "django"]):
        return "python"
    return None


async def run_discover(session: SessionState):
    last_user_message = session.history[-1]["content"]

    # ── NO-OP INTENT (generate directly) ─────────────────────────────────────
    if last_user_message.lower().strip() in ["generate", "generate it", "go ahead", "build it"]:
        session.integration.no_op = False
        session.stage = "generate"

        yield (
            "stage_update",
            {
                "stage": "generate",
                "integration": session.integration.model_dump(),
                "memoryActive": session.memory_active,
            }
        )
        return

    # ── FAST PATH ────────────────────────────────────────────────────────────
    use_case_kw, features_kw = extract_use_case(last_user_message)
    lang_kw = _detect_language(last_user_message)

    prior_use_case = session.integration.useCase
    resolved_use_case = (
        use_case_kw if use_case_kw not in FALLBACK_USE_CASES
        else (prior_use_case or use_case_kw)
    )

    can_fast_path = bool(
        resolved_use_case
        and resolved_use_case not in FALLBACK_USE_CASES
        and lang_kw
    )
    can_fast_path = can_fast_path or bool(prior_use_case and lang_kw)

    if can_fast_path:
        session.integration.useCase = resolved_use_case
        session.integration.language = lang_kw

        existing_features = session.integration.features.copy()
        for f in features_kw:
            if f not in existing_features:
                existing_features.append(f)
        session.integration.features = existing_features

        session.history.append({
            "role": "assistant",
            "content": f"[EXTRACTED] use_case={resolved_use_case} stack={lang_kw} problem=context"
        })

        session.integration.no_op = False
        session.integration.stack = None
        session.integration.architecture = None
        session.integration.feature = None
        session.stage = "match"

        await context_store.upload(
            session.id,
            {
                "useCase": session.integration.useCase,
                "features": session.integration.features,
                "problem": last_user_message[:150],
            }
        )

        yield (
            "stage_update",
            {
                "stage": "match",
                "integration": session.integration.model_dump(),
                "memoryActive": session.memory_active,
            }
        )
        return

    # ── SLOW PATH ────────────────────────────────────────────────────────────
    stored_context = await context_store.search(
        session.id,
        last_user_message
    )

    system = DISCOVER_SYSTEM_PROMPT
    if stored_context:
        memory_block = "\n".join(stored_context)
        system = (
            f"{DISCOVER_SYSTEM_PROMPT}\n\n"
            f"What I already know about this developer:\n{memory_block}"
        )
        session.memory_active = True

    full_response = ""
    pending: list[str] = []
    TRIGGER = "[EXTRACTED]"
    suppressing = False

    async for token in stream_chat(session.history, system):
        full_response += token

        if suppressing:
            continue

        pending.append(token)
        window = "".join(pending)

        if TRIGGER in window:
            before = window[: window.index(TRIGGER)]
            if before.strip():
                yield ("token", {"text": before})
            suppressing = True
            pending = []
            continue

        if not TRIGGER.startswith(window[-len(TRIGGER):]) and len(pending) > len(TRIGGER):
            yield ("token", {"text": "".join(pending)})
            pending = []
        elif len(pending) > len(TRIGGER) * 2:
            flush = "".join(pending[: len(pending) - len(TRIGGER)])
            yield ("token", {"text": flush})
            pending = pending[len(pending) - len(TRIGGER):]

    if pending and not suppressing:
        yield ("token", {"text": "".join(pending)})

    session.history.append({
        "role": "assistant",
        "content": full_response
    })

    extracted = extract_structured(full_response)

    use_case_kw, features_kw = extract_use_case(last_user_message)

    previous_use_case = session.integration.useCase
    existing_features = session.integration.features.copy()

    use_case = extracted.get("use_case") or use_case_kw
    problem = extracted.get("problem")

    if any(word in last_user_message.lower() for word in ["actually", "instead", "make it", "change to"]):
        updated_features = features_kw
    else:
        updated_features = existing_features.copy()
        for f in features_kw:
            if f not in updated_features:
                updated_features.append(f)

    if use_case not in FALLBACK_USE_CASES or session.integration.useCase is None:
        session.integration.useCase = use_case

    session.integration.features = updated_features

    msg_lower = last_user_message.lower()

    if any(kw in msg_lower for kw in ["javascript", "js", "node", "express", "typescript"]):
        session.integration.language = "javascript"
    elif any(kw in msg_lower for kw in ["java", "spring"]):
        session.integration.language = "java"
    elif "python" in msg_lower or any(kw in msg_lower for kw in ["fastapi", "flask", "django"]):
        session.integration.language = "python"

    extracted_stack = extracted.get("stack", "").lower()
    if extracted_stack:
        if any(kw in extracted_stack for kw in ["javascript", "js", "node", "typescript"]):
            session.integration.language = "javascript"
        elif any(kw in extracted_stack for kw in ["java", "spring"]):
            session.integration.language = "java"
        elif any(kw in extracted_stack for kw in ["python", "fastapi", "flask", "django"]):
            session.integration.language = "python"

    has_structured = bool(
        extracted.get("use_case")
        and extracted.get("stack")
        and extracted.get("problem")
    )

    has_stack_keyword = any(kw in msg_lower for kw in STACK_KEYWORDS)
    has_keyword = bool(use_case_kw and has_stack_keyword)

    has_feature = session.integration.feature is not None

    language_changed = False
    if any(word in msg_lower for word in ["actually", "instead", "change", "use", "switch"]):
        if any(kw in msg_lower for kw in STACK_KEYWORDS):
            language_changed = True

    no_new_info = (
        has_feature
        and set(updated_features) == set(existing_features)
        and session.integration.useCase == previous_use_case
        and not language_changed
    )

    if has_structured or has_keyword:
        session.integration.no_op = False
        session.integration.stack = None
        session.integration.architecture = None
        session.integration.feature = None
        session.stage = "match"

    elif no_new_info:
        session.integration.no_op = True
        session.stage = "generate"

    else:
        session.integration.no_op = False
        session.stage = "discover"

    await context_store.upload(
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