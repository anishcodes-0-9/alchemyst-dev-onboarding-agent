from __future__ import annotations
from app.models.session import SessionState
from app.services.llm import stream_chat


GENERATE_PROMPT = """You are generating production-ready {language} code using the latest OpenAI Python SDK.

Use case: {use_case}
Feature: {feature}
Problem: {problem}

STRICT REQUIREMENTS:
- MUST use latest OpenAI SDK syntax
- MUST use: from openai import OpenAI
- MUST use: client.chat.completions.create(...)
- MUST use model: "gpt-4o"

- Streaming MUST follow EXACT pattern:

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

- DO NOT use:
  - dict-style access (chunk['choices'])
  - openai.Chat.create
  - openai.Completion.create
  - text-davinci-003
  - gpt-3.5-turbo

- Use OPENAI_API_KEY from environment
- Max 60 lines
- No markdown
- No 

- For embeddings:
  MUST use: client.embeddings.create(...)
  MUST use model: "text-embedding-3-small"
  DO NOT use openai.embeddings_utils

Return ONLY code.
"""


NARRATIVE_PROMPT = """In 1-2 sentences, explain why this OpenAI-based approach fits the user's use case.

Use case: {use_case}
Feature: {feature}
Stack: {stack}
Problem: {problem}

Be specific and practical. No fluff.

Return ONLY plain text. No quotes.
"""


async def run_generate(session: SessionState, requested_language: str | None = None):
    if requested_language is None:
        requested_language = session.integration.language

    # no_op: feature already set, same language requested
    if (
        session.integration.no_op and
        session.integration.language == requested_language
    ):
        yield (
            "code",
            {
                "snippet": "# Integration already configured — no changes needed.",
                "language": session.integration.language,
            }
        )
        yield ("token", {"text": "Your integration is already set up. Want me to help you deploy it or extend it?"})
        session.stage = "done"
        yield ("done", {"sessionId": session.id})
        return

    session.integration.language = requested_language

    use_case = session.integration.useCase or "chatbot"
    feature  = session.integration.feature or "OpenAI Chat API"
    stack    = session.integration.stack or requested_language
    language = session.integration.language

    # extract the clearest problem statement from conversation history
    problem = "users lose context between sessions"
    for msg in reversed(session.history):
        if msg["role"] == "user" and len(msg["content"].strip()) > 20:
            problem = msg["content"].strip()
            break

    prompt = GENERATE_PROMPT.format(
        use_case=use_case,
        feature=feature,
        stack=stack,
        problem=problem,
        language=language,
    )

    # ── NARRATIVE (before code) ──────────────────────────────────────────────
    # Derive a human-readable stack label from the actual language being generated.
    # Do NOT use session.integration.stack here — it reflects the session's original
    # language and will be wrong after a tab-switch (e.g. Python session → JS regen).
    _stack_labels = {
        "python": "Python / FastAPI",
        "javascript": "Node.js / Express",
        "java": "Java / Spring Boot",
    }
    narrative_stack = _stack_labels.get(language, stack)

    narrative_prompt = NARRATIVE_PROMPT.format(
        use_case=use_case,
        feature=feature,
        stack=narrative_stack,
        problem=problem,
    )
    narrative_parts = []
    async for token in stream_chat(
        messages=[{"role": "user", "content": "Write the narrative now."}],
        system_prompt=narrative_prompt,
        max_tokens=80,
    ):
        narrative_parts.append(token)
        yield ("token", {"text": token})

    # ── CODE ─────────────────────────────────────────────────────────────────
    code_parts = []
    async for token in stream_chat(
        messages=[{"role": "user", "content": "Write the integration code now."}],
        system_prompt=prompt,
        max_tokens=550,
    ):
        code_parts.append(token)

    # strip markdown fences if the LLM adds them despite instructions
    raw = "".join(code_parts).strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    if raw.endswith("```"):
        raw = "\n".join(raw.split("\n")[:-1])
    final_code = raw.strip()

    yield ("code", {"snippet": final_code, "language": language})

    session.stage = "done"
    yield ("done", {"sessionId": session.id})