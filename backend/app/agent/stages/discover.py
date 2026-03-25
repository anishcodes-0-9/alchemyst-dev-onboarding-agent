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


def _detect_language(text: str) -> str | None:
    """Return canonical language string if a stack keyword is found in text."""
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

    # ── FAST PATH ────────────────────────────────────────────────────────────
    # If we can extract all three fields from the current message + session
    # state without asking the LLM, skip the LLM call entirely.
    # This prevents Alex from asking a redundant question when all info is
    # already present (e.g. "RAG pipeline in JavaScript, no memory between searches").
    use_case_kw, features_kw = extract_use_case(last_user_message)
    lang_kw = _detect_language(last_user_message)

    # also check accumulated history for use case if current message only adds stack
    prior_use_case = session.integration.useCase
    resolved_use_case = use_case_kw if use_case_kw not in FALLBACK_USE_CASES else (prior_use_case or use_case_kw)

    # fast-path condition: we have use case + language keyword right now
    # (problem is implicitly "in message" — good enough to advance)
    can_fast_path = bool(
        resolved_use_case
        and resolved_use_case not in FALLBACK_USE_CASES
        and lang_kw
    )
    # also fast-path if previous turn already set use case and this message adds language
    can_fast_path = can_fast_path or bool(prior_use_case and lang_kw)

    if can_fast_path:
        # update state without an LLM call
        session.integration.useCase = resolved_use_case
        session.integration.language = lang_kw
        existing_features = session.integration.features.copy()
        for f in features_kw:
            if f not in existing_features:
                existing_features.append(f)
        session.integration.features = existing_features

        # add a silent assistant turn so history stays consistent
        session.history.append({
            "role": "assistant",
            "content": f"[EXTRACTED] use_case={resolved_use_case} stack={lang_kw} problem=context"
        })

        session.integration.no_op = False
        session.integration.stack = None
        session.integration.architecture = None
        session.integration.feature = None
        session.stage = "match"

        await alchemyst.upload(
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

    # ── SLOW PATH: LLM call needed (missing stack or ambiguous use case) ─────
    # retrieve stored context from Alchemyst memory
    stored_context = await alchemyst.search(
        session.id,
        last_user_message
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
    # buffer tokens until we can confirm [EXTRACTED] is not starting
    # once [EXTRACTED] appears, suppress everything from that point on
    full_response = ""
    pending: list[str] = []   # tokens held while we check for [EXTRACTED]
    TRIGGER = "[EXTRACTED]"
    suppressing = False

    async for token in stream_chat(session.history, system):
        full_response += token

        if suppressing:
            continue

        pending.append(token)
        window = "".join(pending)

        if TRIGGER in window:
            # emit everything before the trigger, then suppress the rest
            before = window[: window.index(TRIGGER)]
            if before.strip():
                yield ("token", {"text": before})
            suppressing = True
            pending = []
            continue

        # if the window can't possibly be a prefix of TRIGGER, flush it
        if not TRIGGER.startswith(window[-len(TRIGGER):]) and len(pending) > len(TRIGGER):
            flush = "".join(pending)
            yield ("token", {"text": flush})
            pending = []
        elif len(pending) > len(TRIGGER) * 2:
            # safety valve — flush oldest tokens
            flush = "".join(pending[: len(pending) - len(TRIGGER)])
            yield ("token", {"text": flush})
            pending = pending[len(pending) - len(TRIGGER):]

    # flush anything remaining (if [EXTRACTED] never appeared)
    if pending and not suppressing:
        yield ("token", {"text": "".join(pending)})

    # add assistant turn to history
    session.history.append({
        "role": "assistant",
        "content": full_response
    })

    # primary: structured [EXTRACTED] block from LLM response
    extracted = extract_structured(full_response)

    # fallback: keyword scan of the user's message
    # (last_user_message defined at top of function)
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

    # detect and set language from message keywords
    msg_lower_lang = last_user_message.lower()
    if any(kw in msg_lower_lang for kw in ["javascript", "js", "node", "express", "typescript"]):
        session.integration.language = "javascript"
    elif any(kw in msg_lower_lang for kw in ["java", "spring"]):
        session.integration.language = "java"
    elif "python" in msg_lower_lang or any(kw in msg_lower_lang for kw in ["fastapi", "flask", "django"]):
        session.integration.language = "python"
    # if no language keyword found, keep existing language

    # also check structured extraction for stack
    extracted_stack = extracted.get("stack", "").lower()
    if extracted_stack:
        if any(kw in extracted_stack for kw in ["javascript", "js", "node", "typescript"]):
            session.integration.language = "javascript"
        elif any(kw in extracted_stack for kw in ["java", "spring"]):
            session.integration.language = "java"
        elif any(kw in extracted_stack for kw in ["python", "fastapi", "flask", "django"]):
            session.integration.language = "python"

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
    language_changed = False
    # check if user is explicitly correcting the stack/language
    msg_lower_check = last_user_message.lower()
    if any(word in msg_lower_check for word in ["actually", "instead", "change", "use", "switch"]):
        if any(kw in msg_lower_check for kw in STACK_KEYWORDS):
            language_changed = True

    no_new_info = (
        has_feature
        and set(updated_features) == set(existing_features)
        and final_use_case == previous_use_case
        and not language_changed
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