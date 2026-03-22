import uuid

sessions = {}


from typing import Optional

def get_or_create_session(session_id: Optional[str]):
    if session_id and session_id in sessions:
        return sessions[session_id]

    new_id = session_id or str(uuid.uuid4())

    sessions[new_id] = {
        "id": new_id,
        "stage": "discover",
        "history": [],
        "integration": {
            "useCase": None,
            "stack": None,
            "feature": None,
            "code": None,
        },
    }

    return sessions[new_id]