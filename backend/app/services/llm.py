from __future__ import annotations
import os
from openai import AsyncOpenAI
from typing import AsyncGenerator

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    # When you get Alchemyst key, replace the two lines above with:
    # api_key=os.getenv("ALCHEMYST_API_KEY"),
    # base_url="https://api.getalchemystai.com/v1",
)


async def stream_chat(
    messages: list[dict],
    system_prompt: str
) -> AsyncGenerator[str, None]:
    """Stream tokens from the LLM one by one."""
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            *messages
        ],
        stream=True,
        temperature=0.7,
        max_tokens=1000,
    )
    async for chunk in response:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content