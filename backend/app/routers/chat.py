from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
import json

from app.session_store import get_or_create_session
from app.agent.loop import AgentLoop

router = APIRouter()


@router.post("/chat")
async def chat(request: Request):
    body = await request.json()

    session_id = body.get("sessionId")
    message = body.get("message", "")

    session = get_or_create_session(session_id)
    agent = AgentLoop(session)

    async def event_generator():
        async for event_type, payload in agent.run(message):
            yield {
                "event": event_type,
                "data": json.dumps(payload)
            }

    return EventSourceResponse(event_generator())