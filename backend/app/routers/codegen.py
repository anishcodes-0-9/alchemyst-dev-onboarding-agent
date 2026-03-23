from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import json

from app.session_store import sessions
from app.agent.stages.generate import run_generate

router = APIRouter()


@router.post("/generate-code")
async def generate_code(request: Request):
    body = await request.json()

    session_id = body.get("sessionId")
    language = body.get("language", "python")

    if not session_id or session_id not in sessions:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )

    session = sessions[session_id]

    if not session.integration.feature:
        return JSONResponse(
            status_code=400,
            content={"error": "No feature detected yet. Complete discovery first."}
        )

    # update language and re-run generate
    session.integration.language = language
    session.stage = "generate"

    async def event_generator():
        try:
            async for event_type, payload in run_generate(session):
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