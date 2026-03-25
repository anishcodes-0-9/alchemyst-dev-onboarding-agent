from __future__ import annotations
from app.models.session import SessionState
from app.services.llm import stream_chat


GENERATE_PROMPT = """You are a senior software engineer writing a complete, production-quality integration.

Context:
- Use case: {use_case}
- Feature pattern: {feature}
- Developer's stack: {stack}
- Problem to solve: {problem}
- Language: {language}

Feature pattern definitions:
- IntelliChat: a streaming conversational AI that retains full message history across turns,
  so the user never has to repeat context. Use the OpenAI chat completions API with stream=True,
  maintain a running `messages` list, append each user+assistant turn before the next call.
- ContextAPI: a context storage and retrieval system. Implement upload(user_id, content) that
  stores text with a simple embedding (use sentence hash or keyword index), and search(user_id, query)
  that returns the top 3 most relevant stored documents. No external vector DB needed — use a dict.
- ContextRouter: an OpenAI-compatible proxy layer. Show a real chat completion call using the
  OpenAI SDK with OPENAI_API_KEY from env. Include a clearly commented block showing exactly
  what two lines change when the developer wants to route through a different provider later.

Code requirements:
- Start with a 3-line comment block: line 1 = what this integration does, line 2 = which pattern
  it implements, line 3 = what problem it solves for the user
- Use os.environ["OPENAI_API_KEY"] for Python or process.env.OPENAI_API_KEY for JS/Java
- Every function must be complete — no pass, no ellipsis, no TODO, no raise NotImplementedError
- Include a runnable main block (if __name__ == "__main__" or equivalent) with a realistic example
- Real logic: IntelliChat must show actual streaming output, ContextAPI must show actual
  upload + search round-trip, ContextRouter must show actual completion call
- Use OpenAI SDK v1+ syntax: client = OpenAI(api_key=...); client.chat.completions.create(...) — NOT the old openai.ChatCompletion.create() syntax
- Maximum 65 lines

Return ONLY the code. No markdown fences. No prose before or after."""


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

    completion_text = (
        f"You now have a working {language} starter for the {feature} pattern. "
        f"Want me to help you deploy this or extend it with additional features?"
    )
    yield ("token", {"text": completion_text})

    session.stage = "done"
    yield ("done", {"sessionId": session.id})