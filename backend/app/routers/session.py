from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.session_store import sessions
from app.services.alchemyst import alchemyst

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

    del sessions[session_id]
    await alchemyst.delete(session_id)
    return {"success": True}