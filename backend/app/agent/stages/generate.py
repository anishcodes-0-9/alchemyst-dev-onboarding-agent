from __future__ import annotations
from app.models.session import SessionState
from app.services.llm import stream_chat


GENERATE_PROMPT = """You are writing a {language} integration that calls Alchemyst AI's real HTTP API.

Use case: {use_case}
Feature: {feature}
Problem: {problem}

ALCHEMYST API — these are the REAL endpoints to call:

IntelliChat (streaming chat with automatic session memory):
  POST https://api.getalchemystai.com/v1/chat/completions
  Header: Authorization: Bearer $ALCHEMYST_API_KEY
  Body:   {{"model": "alchemyst-chat", "messages": [...], "stream": true, "user": "<session_id>"}}
  The `user` field scopes memory to a session — Alchemyst injects prior context automatically.
  Python: use AsyncOpenAI(base_url="https://api.getalchemystai.com/v1", api_key=os.environ["ALCHEMYST_API_KEY"])
  JS:     use new OpenAI({{ apiKey: process.env.ALCHEMYST_API_KEY, baseURL: "https://api.getalchemystai.com/v1" }})
  Java:   POST with OkHttp/WebClient to that URL, parse SSE lines

ContextAPI (semantic storage + retrieval, no vector DB needed):
  UPLOAD: POST https://api.getalchemystai.com/context/upload
          Body: {{"userId": str, "content": str, "tags": ["<tag>"]}}
  SEARCH: POST https://api.getalchemystai.com/context/search
          Body: {{"userId": str, "query": str, "top_k": 5}}
          Returns: [{{"content": str, "score": float}}]
  Python: httpx.AsyncClient or requests. Header: Authorization: Bearer $ALCHEMYST_API_KEY
  JS:     fetch() with Authorization header. Base: https://api.getalchemystai.com
  Java:   RestTemplate or WebClient. Header: Bearer $ALCHEMYST_API_KEY

ContextRouter (drop-in OpenAI proxy — zero code changes beyond config):
  Python: client = OpenAI(base_url="https://api.getalchemystai.com/v1", api_key=os.environ["ALCHEMYST_API_KEY"])
  JS:     new OpenAI({{ apiKey: process.env.ALCHEMYST_API_KEY, baseURL: "https://api.getalchemystai.com/v1" }})
  Java:   change base URL only in your client config
  Show a commented BEFORE block (OpenAI config), then the AFTER (Alchemyst config), then a real call.

STRICT RULES:
- DO NOT define fake ContextAPI, IntelliChat, or ContextRouter classes — call the real HTTP endpoints above
- Use OPENAI_API_KEY if you cannot use ALCHEMYST_API_KEY
- 3-line comment block at top:
    # What:    <one line describing what this code does for {use_case}>
    # Feature: {feature}
    # Solves:  <their specific problem in one line>
- Use domain-fitting variable names (user_id, session_id, query, doc_content — NOT "example_user")
- Complete end-to-end example showing actual upload + query (ContextAPI) or actual stream (IntelliChat/ContextRouter)
- All secrets via os.environ / process.env
- No TODOs, no ellipsis, no stub functions
- Max 60 lines

Return ONLY the code. No markdown fences. No explanation text."""


NARRATIVE_PROMPT = """In 1-2 sentences, tell a developer why you chose a specific integration pattern for their use case.
Be direct and specific — name the pattern, their stack, and the exact reason it fits their problem.

Use case: {use_case}
Feature chosen: {feature}
Language/stack: {stack}
Problem: {problem}

Examples of good narrative (no quotes around them — output plain prose):
- You're building a Python chatbot with session memory — IntelliChat is the right fit because it handles streaming and maintains conversation history natively, so you don't have to manage message arrays yourself.
- For a RAG pipeline in Node.js, Context API gives you upload + semantic search out of the box — no vector database setup required.
- Since you're replacing an existing OpenAI integration in Spring Boot, Context Router is the cleanest path — it's a drop-in proxy, so your existing code needs zero changes.

IMPORTANT: Do NOT wrap your response in quotation marks. Output plain prose only.
Return ONLY the 1-2 sentence narrative. No intro, no sign-off, no code."""


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
    feature  = session.integration.feature or "IntelliChat"
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