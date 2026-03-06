"""
runner/session.py
──────────────────
Session service factory.
Currently wraps InMemorySessionService; swap to a persistent backend
(e.g., FirestoreSessionService) here without touching any other module.
"""

from __future__ import annotations

from google.adk.sessions import InMemorySessionService

from config.settings import get_settings
from utils.logger import get_logger

logger   = get_logger(__name__)
settings = get_settings()

# Module-level singleton — one session service per process lifetime
_session_service: InMemorySessionService | None = None


def get_session_service() -> InMemorySessionService:
    """Return the shared session service instance (created once)."""
    global _session_service
    if _session_service is None:
        logger.info("Initialising InMemorySessionService for app: %s", settings.app_name)
        _session_service = InMemorySessionService()
    return _session_service


async def create_session(user_id: str | None = None) -> object:
    """
    Create and return a new ADK session.

    Args:
        user_id: Optional override; defaults to settings.default_user_id.
    """
    svc     = get_session_service()
    uid     = user_id or settings.default_user_id
    session = await svc.create_session(app_name=settings.app_name, user_id=uid)
    logger.info("Session created: id=%s  user=%s", session.id, uid)
    return session