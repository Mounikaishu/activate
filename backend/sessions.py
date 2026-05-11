"""
Placement Reality Check — In-memory session management.
Stores resume text, JD text, analysis results, and interview history per session.
"""

import uuid
from typing import Optional

# In-memory session store
_sessions: dict[str, dict] = {}


def create_session(resume_text: str, jd_text: str) -> str:
    """Create a new analysis session and return its ID."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "resume_text": resume_text,
        "jd_text": jd_text,
        "analysis": None,
        "skill_gaps": None,
        "improvements": None,
        "verdict": None,
        "interview_history": [],
    }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """Get session data by ID."""
    return _sessions.get(session_id)


def update_session(session_id: str, **kwargs):
    """Update session fields."""
    if session_id in _sessions:
        _sessions[session_id].update(kwargs)


def delete_session(session_id: str):
    """Delete a session."""
    _sessions.pop(session_id, None)


def get_all_sessions() -> dict:
    """Return all sessions (for debugging)."""
    return _sessions
