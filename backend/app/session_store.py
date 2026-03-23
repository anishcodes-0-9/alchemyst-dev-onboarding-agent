from __future__ import annotations
from typing import Optional
from app.models.session import SessionState, IntegrationState


sessions: dict[str, SessionState] = {}


def get_or_create_session(session_id: Optional[str]) -> SessionState:
    if session_id and session_id in sessions:
        return sessions[session_id]

    # do NOT pass id=None — let the factory generate it
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
    return session