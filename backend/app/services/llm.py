from __future__ import annotations
import os
from openai import AsyncOpenAI
from typing import AsyncGenerator

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)


async def stream_chat(
    messages: list[dict],
    system_prompt: str | None = None,
    max_tokens: int = 600,
) -> AsyncGenerator[str, None]:
    """Stream tokens from the LLM one by one."""

    final_messages = messages
    if system_prompt:
        final_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=final_messages,
        stream=True,
        temperature=0.2,
        max_tokens=max_tokens,
    )

    async for chunk in response:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta and getattr(delta, "content", None):
            yield delta.content