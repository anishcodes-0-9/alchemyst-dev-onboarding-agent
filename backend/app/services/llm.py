from __future__ import annotations
import os
from openai import AsyncOpenAI
from typing import AsyncGenerator

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


async def stream_chat(
    messages: list[dict],
    system_prompt: str,
    max_tokens: int = 600,
) -> AsyncGenerator[str, None]:
    """Stream tokens from the LLM one by one."""
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            *messages
        ],
        stream=True,
        temperature=0.3,
        max_tokens=max_tokens,
    )
    async for chunk in response:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content