from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.session_store import sessions, session_locks
from app.services.context_store import context_store

router = APIRouter()


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    return {
        "sessionId": session.id,
        "stage": session.stage,
        "integration": session.integration.model_dump(),
        "memoryActive": session.memory_active,
        "historyLength": len(session.history),
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    await context_store.delete(session_id)

    del sessions[session_id]

# cleanup lock (important)
    if session_id in session_locks:
        del session_locks[session_id]

    return {"success": True}