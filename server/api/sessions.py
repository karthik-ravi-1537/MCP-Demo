"""Session management for the API."""

import secrets
import time

from fastapi import Cookie, Depends, HTTPException, Response
from pydantic import BaseModel

# In-memory session store (would use Redis or similar in production)
sessions: dict[str, dict] = {}


class SessionData(BaseModel):
    """Session data model."""

    user_id: str
    created_at: float
    last_active: float
    data: dict = {}


def create_session(response: Response, user_id: str) -> str:
    """Create a new session.

    Args:
        response: FastAPI response object to set the cookie.
        user_id: ID of the user.

    Returns:
        Session ID.
    """
    # Generate a random session ID
    session_id = secrets.token_urlsafe(32)

    # Create the session
    sessions[session_id] = {
        "user_id": user_id,
        "created_at": time.time(),
        "last_active": time.time(),
        "data": {},
    }

    # Set the session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=3600 * 24 * 7,  # 7 days
        samesite="lax",
    )

    return session_id


def get_session(session_id: str | None = Cookie(None, alias="session_id")) -> SessionData | None:
    """Get the current session.

    Args:
        session_id: Session ID from cookie.

    Returns:
        Session data, or None if no session.
    """
    if session_id is None or session_id not in sessions:
        return None

    # Update last active time
    sessions[session_id]["last_active"] = time.time()

    return SessionData(**sessions[session_id])


def get_active_session(session: SessionData | None = Depends(get_session)) -> SessionData:
    """Get the current active session, or raise an error.

    Args:
        session: Session data from get_session.

    Returns:
        Session data.

    Raises:
        HTTPException: If no active session.
    """
    if session is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return session


def end_session(response: Response, session_id: str | None = Cookie(None, alias="session_id")) -> None:
    """End the current session.

    Args:
        response: FastAPI response object to clear the cookie.
        session_id: Session ID from cookie.
    """
    if session_id is not None and session_id in sessions:
        del sessions[session_id]

    response.delete_cookie(key="session_id")


def cleanup_sessions() -> None:
    """Clean up expired sessions."""
    now = time.time()
    expired = []

    for session_id, session in sessions.items():
        # Sessions expire after 7 days of inactivity
        if now - session["last_active"] > 3600 * 24 * 7:
            expired.append(session_id)

    for session_id in expired:
        del sessions[session_id]
