"""
Unit Tests for the Session Memory Store
"""

import threading
from datetime import datetime, timedelta, UTC

from langchain_core.messages import HumanMessage, AIMessage

from services.memory import SessionStore


def test_new_session_returns_empty_history():
    """A session that was never written returns an empty list"""
    store = SessionStore()
    assert store.get_history("new-id") == []


def test_add_exchange_stores_messages():
    """Adding an exchange stores one human and one AI message"""
    store = SessionStore()
    store.add_exchange("s1", "hello", "hi there")

    history = store.get_history("s1")
    assert len(history) == 2
    assert isinstance(history[0], HumanMessage)
    assert history[0].content == "hello"
    assert isinstance(history[1], AIMessage)
    assert history[1].content == "hi there"


def test_window_limit_enforced():
    """After 7 exchanges only the last 6 (12 messages) remain"""
    store = SessionStore(max_window=6)
    for i in range(7):
        store.add_exchange("s1", f"q{i}", f"a{i}")

    history = store.get_history("s1")
    assert len(history) == 12
    # Oldest exchange (q0/a0) should have dropped off
    assert history[0].content == "q1"
    assert history[-1].content == "a6"


def test_sessions_are_isolated():
    """Messages in one session are not visible in another"""
    store = SessionStore()
    store.add_exchange("a", "question a", "answer a")
    store.add_exchange("b", "question b", "answer b")

    history_a = store.get_history("a")
    history_b = store.get_history("b")

    assert len(history_a) == 2
    assert len(history_b) == 2
    assert history_a[0].content == "question a"
    assert history_b[0].content == "question b"


def test_expired_session_cleaned_up():
    """A session older than the TTL is removed on cleanup"""
    store = SessionStore(ttl_seconds=3600)
    store.add_exchange("s1", "q", "a")

    # Force the session's last_accessed timestamp into the past
    store._sessions["s1"].last_accessed = datetime.now(UTC) - timedelta(seconds=7200)

    store.cleanup_expired()
    assert store.get_history("s1") == []


def test_get_history_returns_copy():
    """Mutating the returned history does not affect the store"""
    store = SessionStore()
    store.add_exchange("s1", "q", "a")

    history = store.get_history("s1")
    history.append(HumanMessage(content="injected"))

    assert len(store.get_history("s1")) == 2


def test_clear_removes_session():
    """clear() removes a session entirely"""
    store = SessionStore()
    store.add_exchange("s1", "q", "a")
    store.clear("s1")
    assert store.get_history("s1") == []


def test_thread_safety():
    """Concurrent reads and writes do not crash or corrupt state"""
    store = SessionStore(max_window=6)

    def worker(session_id: str):
        for i in range(50):
            store.add_exchange(session_id, f"q{i}", f"a{i}")
            store.get_history(session_id)

    threads = [
        threading.Thread(target=worker, args=(f"session-{n}",))
        for n in range(8)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Every session should respect the window limit
    for n in range(8):
        assert len(store.get_history(f"session-{n}")) == 12
