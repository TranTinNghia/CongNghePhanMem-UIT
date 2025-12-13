from datetime import datetime, timedelta
from typing import Optional
import threading
class VisitCountService:
    _active_sessions = {}
    _lock = threading.Lock()
    _timeout_minutes = 5
    @classmethod
    def _cleanup_old_sessions(cls):
        now = datetime.now()
        timeout = timedelta(minutes=cls._timeout_minutes)
        with cls._lock:
            expired_sessions = [
                session_id for session_id, last_activity in cls._active_sessions.items()
                if now - last_activity > timeout
            ]
            for session_id in expired_sessions:
                del cls._active_sessions[session_id]
    @classmethod
    def get_active_visit_count(cls) -> Optional[int]:
        cls._cleanup_old_sessions()
        with cls._lock:
            return len(cls._active_sessions)
    @classmethod
    def record_visit(cls, session_id: str) -> bool:
        try:
            with cls._lock:
                cls._active_sessions[session_id] = datetime.now()
            cls._cleanup_old_sessions()
            return True
        except Exception as e:
            print(f"[VisitCountService] Error recording visit: {e}")
            return False
