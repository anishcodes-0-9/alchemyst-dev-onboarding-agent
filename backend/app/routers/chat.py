from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import json

from app.session_store import get_or_create_session
from app.agent.loop import AgentLoop

router = APIRouter()


@router.post("/chat")
async def chat(request: Request):
    body = await request.json()

    session_id = body.get("sessionId")
    message = body.get("message")
    language = body.get("language", "python")

    if not message or not message.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "message is required"}
        )

    session = get_or_create_session(session_id)

    # sync language choice into session
    session.integration.language = language

    agent = AgentLoop(session)

    async def event_generator():
        try:
            async for event_type, payload in agent.run(message):
                yield {
                    "event": event_type,
                    "data": json.dumps(payload)
                }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }

    return EventSourceResponse(event_generator())