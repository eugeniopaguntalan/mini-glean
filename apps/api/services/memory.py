"""
Memory Service
In-memory session store for multi-turn conversation history with TTL expiration
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from typing import Dict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


@dataclass
class SessionData:
    """Stored conversation state for a single session"""
    messages: List[BaseMessage] = field(default_factory=list)
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))


class SessionStore:
    """
    Thread-safe in-memory store for conversation sessions.

    - Keeps the last `max_window` exchanges per session (1 exchange = 2 messages)
    - Sessions expire after `ttl_seconds` of inactivity
    """

    def __init__(self, max_window: int = 6, ttl_seconds: int = 3600):
        self.max_window = max_window
        self.ttl_seconds = ttl_seconds
        self._sessions: Dict[str, SessionData] = {}
        self._lock = threading.Lock()

    def get_history(self, session_id: str) -> List[BaseMessage]:
        """
        Get the message history for a session

        Args:
            session_id: The session identifier

        Returns:
            List of LangChain messages (empty if session does not exist)
        """
        with self._lock:
            self._cleanup_expired_locked()

            session = self._sessions.get(session_id)
            if session is None:
                return []

            session.last_accessed = datetime.now(UTC)
            # Return a copy so callers cannot mutate internal state
            return list(session.messages)

    def add_exchange(
        self,
        session_id: str,
        user_msg: str,
        assistant_msg: str,
    ) -> None:
        """
        Add a user/assistant exchange to a session, enforcing the window limit

        Args:
            session_id: The session identifier
            user_msg: The user's message
            assistant_msg: The assistant's response
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = SessionData()
                self._sessions[session_id] = session

            session.messages.append(HumanMessage(content=user_msg))
            session.messages.append(AIMessage(content=assistant_msg))
            session.last_accessed = datetime.now(UTC)

            # Enforce window: keep at most max_window exchanges (2 messages each)
            max_messages = self.max_window * 2
            if len(session.messages) > max_messages:
                session.messages = session.messages[-max_messages:]

    def clear(self, session_id: str) -> None:
        """
        Remove a session entirely

        Args:
            session_id: The session identifier
        """
        with self._lock:
            self._sessions.pop(session_id, None)

    def cleanup_expired(self) -> None:
        """Remove all sessions that have exceeded the TTL"""
        with self._lock:
            self._cleanup_expired_locked()

    def _cleanup_expired_locked(self) -> None:
        """Internal cleanup — caller must already hold the lock"""
        now = datetime.now(UTC)
        cutoff = timedelta(seconds=self.ttl_seconds)
        expired = [
            sid
            for sid, data in self._sessions.items()
            if now - data.last_accessed > cutoff
        ]
        for sid in expired:
            del self._sessions[sid]


# Module-level singleton used by the agent service
session_store = SessionStore()
