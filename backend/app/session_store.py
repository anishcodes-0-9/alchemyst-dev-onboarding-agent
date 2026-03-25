from __future__ import annotations
from typing import Optional
import asyncio

from app.models.session import SessionState, IntegrationState


sessions: dict[str, SessionState] = {}
session_locks: dict[str, asyncio.Lock] = {}


def get_or_create_session(session_id: Optional[str]) -> SessionState:
    if session_id and session_id in sessions:
        return sessions[session_id]

    if session_id:
        session = SessionState(
            id=session_id,
            integration=IntegrationState()
        )
    else:
        session = SessionState(
            integration=IntegrationState()
        )

    sessions[session.id] = session
    session_locks[session.id] = asyncio.Lock()  # ✅ create lock

    return session