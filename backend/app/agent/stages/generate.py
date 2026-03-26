from __future__ import annotations
from app.models.session import SessionState
from app.services.llm import stream_chat


GENERATE_PROMPT = """You are a senior software engineer. Write complete, production-quality code.

Language: {language}
Use case: {use_case}
Feature: {feature}
Problem: {problem}

STRICT RULE:
- If use_case = backend:
  DO NOT use OpenAI anywhere.
  Build a standard backend API only.

IMPORTANT:
- If the use case is "backend" or "api":
  - DO NOT use OpenAI
  - Build a standard backend (REST API, controllers, routes, services)

LANGUAGE RULES — these are absolute, no exceptions:
- If language=python: use Python syntax only. Use FastAPI if backend.
- If language=javascript: use Node.js/Express only.
- If language=java: use Java with Spring Boot.

APPLY THE FOLLOWING ONLY IF use_case IS chatbot, rag, or agent:

OPENAI SDK RULES:
- Python: `client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])`
- JavaScript: `const openai = new OpenAI({{ apiKey: process.env.OPENAI_API_KEY }})`
- Java: Use RestTemplate or WebClient with Bearer token

FEATURE IMPLEMENTATION:
- chatbot: maintain messages[] across turns
- rag: implement simple document store + search
- agent: implement basic tool loop

CODE REQUIREMENTS:
- First 3 lines: comments explaining what this does
- No placeholders, no TODOs
- Include main/example usage
- Max 65 lines
- NO markdown fences

Return ONLY the code."""


NARRATIVE_PROMPT = """Explain the system or backend approach for solving this problem.
Do not mention OpenAI unless required.

Use case: {use_case}
Feature: {feature}
Stack: {stack}
Problem: {problem}

Return ONLY plain text."""


_STACK_LABELS = {
    "python": "Python / FastAPI",
    "javascript": "Node.js / Express",
    "java": "Java / Spring Boot",
}


async def run_generate(session: SessionState, requested_language: str | None = None):
    if requested_language is None:
        requested_language = session.integration.language

    # no_op path
    if session.integration.no_op and session.integration.language == requested_language:
        yield ("code", {
            "snippet": "# Integration already configured — no changes needed.",
            "language": session.integration.language,
        })
        yield ("token", {"text": "Your integration is already set up. Want help extending it?"})
        session.stage = "done"
        yield ("done", {"sessionId": session.id})
        return

    # ✅ only set language if not already present
    if not session.integration.language:
        session.integration.language = requested_language

    # ---------------- CORE LOGIC ----------------

    language = session.integration.language or requested_language
    problem = " ".join([
    msg["content"] for msg in session.history[-3:]
    if msg["role"] == "user"
])

    msg_lower = problem.lower()

    # language override
    # ONLY override if session has no language yet
    # language override
# ONLY override if user explicitly mentions language
    if any(word in msg_lower for word in ["node", "javascript", "java", "python"]):
        if "node" in msg_lower or "javascript" in msg_lower:
            language = "javascript"
        elif "java" in msg_lower:
            language = "java"
        elif "python" in msg_lower:
            language = "python"

    # stack AFTER language fix
    stack = _STACK_LABELS.get(language, language)

    # detect use case
    use_case = session.integration.useCase
    feature = session.integration.feature

    if "rag" in msg_lower:
        use_case = "rag"
    elif "agent" in msg_lower:
        use_case = "agent"
    elif "chatbot" in msg_lower:
        use_case = "chatbot"
    elif "api" in msg_lower or "backend" in msg_lower:
        use_case = "backend"
        # ✅ LOCK use_case from session (prevents reset in multi-turn)
    if session.integration.useCase:
        use_case = session.integration.useCase

    # fallback
    if not use_case:
        use_case = "backend"

    if not feature:
        feature = "standard API"

    # ---------------- NARRATIVE ----------------

    narrative_prompt = NARRATIVE_PROMPT.format(
        use_case=use_case,
        feature=feature,
        stack=stack,
        problem=problem,
    )

    async for token in stream_chat(
        messages=[{"role": "user", "content": problem}],
        system_prompt=narrative_prompt,
        max_tokens=80,
    ):
        yield ("token", {"text": token})

    # ---------------- CODE ----------------

    code_prompt = GENERATE_PROMPT.format(
        language=language,
        use_case=use_case,
        feature=feature,
        problem=problem,
    )

    code_parts = []
    async for token in stream_chat(
        messages=[{"role": "user", "content": problem}],
        system_prompt=code_prompt,
        max_tokens=600,
    ):
        code_parts.append(token)

    raw = "".join(code_parts).strip()

    # strip markdown fences
    lines = raw.split("\n")
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    final_code = "\n".join(lines).strip()

    yield ("code", {"snippet": final_code, "language": language})

    completion_text = (
        f"You now have a working {language} solution for a {use_case}. "
        f"Want help extending it or deploying it?"
    )
    yield ("token", {"text": completion_text})

    session.stage = "done"
    yield ("done", {"sessionId": session.id})