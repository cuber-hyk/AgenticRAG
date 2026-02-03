from typing import Dict
from dataclasses import dataclass, field
import threading


@dataclass
class Session:
    id: str
    history: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class SessionStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._sessions: Dict[str, Session] = {}

    def get_or_create(self, session_id: str) -> Session:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = Session(id=session_id)
            return self._sessions[session_id]


_store = SessionStore()


def get_session_store():
    return _store
