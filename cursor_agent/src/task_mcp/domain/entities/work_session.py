"""WorkSession Domain Entity"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


class SessionStatus(Enum):
    """Work session status enumeration"""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class WorkSession:
    """WorkSession entity representing an active work session by an agent on a task"""

    id: str
    agent_id: str
    task_id: str
    tree_id: str
    started_at: datetime

    # Session status and timing
    status: SessionStatus = SessionStatus.ACTIVE
    ended_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    total_paused_duration: timedelta = field(default_factory=lambda: timedelta(0))

    # Session metadata
    session_notes: str = ""
    progress_updates: List[Dict] = field(default_factory=list)
    resources_locked: List[str] = field(default_factory=list)

    # Session configuration
    max_duration: Optional[timedelta] = None  # Auto-timeout after this duration
    auto_save_interval: int = 300  # Seconds between auto-saves
    last_activity: datetime = field(default_factory=datetime.now)

    def pause_session(self, reason: str = "") -> None:
        """Pause the work session"""
        if self.status != SessionStatus.ACTIVE:
            raise ValueError(f"Cannot pause session in {self.status.value} state")

        self.status = SessionStatus.PAUSED
        self.paused_at = datetime.now()
        self.last_activity = datetime.now()

        if reason:
            self.add_progress_update("session_paused", f"Session paused: {reason}")

    def resume_session(self) -> None:
        """Resume a paused work session"""
        if self.status != SessionStatus.PAUSED:
            raise ValueError(f"Cannot resume session in {self.status.value} state")

        if self.paused_at:
            # Add paused time to total
            paused_duration = datetime.now() - self.paused_at
            self.total_paused_duration += paused_duration
            self.paused_at = None

        self.status = SessionStatus.ACTIVE
        self.last_activity = datetime.now()
        self.add_progress_update("session_resumed", "Session resumed")

    def complete_session(self, success: bool = True, notes: str = "") -> None:
        """Complete the work session"""
        if self.status not in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            raise ValueError(f"Cannot complete session in {self.status.value} state")

        self.status = SessionStatus.COMPLETED
        self.ended_at = datetime.now()
        self.last_activity = datetime.now()

        if notes:
            self.session_notes += f"\nCompletion notes: {notes}"

        completion_type = "successful" if success else "unsuccessful"
        self.add_progress_update(
            "session_completed", f"Session completed ({completion_type})"
        )

    def cancel_session(self, reason: str = "") -> None:
        """Cancel the work session"""
        self.status = SessionStatus.CANCELLED
        self.ended_at = datetime.now()
        self.last_activity = datetime.now()

        if reason:
            self.session_notes += f"\nCancellation reason: {reason}"

        self.add_progress_update("session_cancelled", f"Session cancelled: {reason}")

    def timeout_session(self) -> None:
        """Timeout the work session due to inactivity or max duration"""
        self.status = SessionStatus.TIMEOUT
        self.ended_at = datetime.now()

        self.add_progress_update("session_timeout", "Session timed out")

    def add_progress_update(
        self, update_type: str, message: str, metadata: Dict = None
    ) -> None:
        """Add a progress update to the session"""
        update = {
            "timestamp": datetime.now().isoformat(),
            "type": update_type,
            "message": message,
            "metadata": metadata or {},
        }

        self.progress_updates.append(update)
        self.last_activity = datetime.now()

    def lock_resource(self, resource_id: str) -> None:
        """Lock a resource for this session"""
        if resource_id not in self.resources_locked:
            self.resources_locked.append(resource_id)
            self.add_progress_update(
                "resource_locked", f"Locked resource: {resource_id}"
            )

    def unlock_resource(self, resource_id: str) -> None:
        """Unlock a resource from this session"""
        if resource_id in self.resources_locked:
            self.resources_locked.remove(resource_id)
            self.add_progress_update(
                "resource_unlocked", f"Unlocked resource: {resource_id}"
            )

    def unlock_all_resources(self) -> None:
        """Unlock all resources held by this session"""
        for resource_id in self.resources_locked.copy():
            self.unlock_resource(resource_id)

    def get_active_duration(self) -> timedelta:
        """Get the total active duration (excluding paused time)"""
        if self.status == SessionStatus.ACTIVE:
            total_duration = datetime.now() - self.started_at
        elif self.ended_at:
            total_duration = self.ended_at - self.started_at
        else:
            total_duration = timedelta(0)

        return total_duration - self.total_paused_duration

    def get_total_duration(self) -> timedelta:
        """Get the total duration including paused time"""
        if self.status == SessionStatus.ACTIVE:
            return datetime.now() - self.started_at
        elif self.ended_at:
            return self.ended_at - self.started_at
        else:
            return timedelta(0)

    def is_active(self) -> bool:
        """Check if the session is currently active"""
        return self.status == SessionStatus.ACTIVE

    def is_timeout_due(self) -> bool:
        """Check if the session should be timed out"""
        if not self.max_duration:
            return False

        return self.get_total_duration() > self.max_duration

    def get_session_summary(self) -> Dict:
        """Get a comprehensive summary of the work session"""
        return {
            "session_id": self.id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "tree_id": self.tree_id,
            "status": self.status.value,
            "timing": {
                "started_at": self.started_at.isoformat(),
                "ended_at": self.ended_at.isoformat() if self.ended_at else None,
                "paused_at": self.paused_at.isoformat() if self.paused_at else None,
                "last_activity": self.last_activity.isoformat(),
                "active_duration": str(self.get_active_duration()),
                "total_duration": str(self.get_total_duration()),
                "total_paused_duration": str(self.total_paused_duration),
            },
            "progress": {
                "total_updates": len(self.progress_updates),
                "latest_update": (
                    self.progress_updates[-1] if self.progress_updates else None
                ),
                "session_notes": self.session_notes,
            },
            "resources": {
                "locked_resources": self.resources_locked,
                "total_locked": len(self.resources_locked),
            },
            "configuration": {
                "max_duration": str(self.max_duration) if self.max_duration else None,
                "auto_save_interval": self.auto_save_interval,
                "timeout_due": self.is_timeout_due(),
            },
        }

    def get_progress_timeline(self) -> List[Dict]:
        """Get a chronological timeline of all progress updates"""
        return sorted(self.progress_updates, key=lambda x: x["timestamp"])

    def extend_session(self, additional_duration: timedelta) -> None:
        """Extend the maximum duration of the session"""
        if self.max_duration:
            self.max_duration += additional_duration
        else:
            self.max_duration = additional_duration

        self.add_progress_update(
            "session_extended", f"Session extended by {additional_duration}"
        )

    def update_activity(self) -> None:
        """Update the last activity timestamp"""
        self.last_activity = datetime.now()

    @classmethod
    def create_session(
        cls,
        agent_id: str,
        task_id: str,
        tree_id: str,
        max_duration_hours: Optional[float] = None,
    ) -> "WorkSession":
        """Factory method to create a new work session"""
        session_id = f"{agent_id}_{task_id}_{datetime.now().timestamp()}"

        max_duration = None
        if max_duration_hours:
            max_duration = timedelta(hours=max_duration_hours)

        session = cls(
            id=session_id,
            agent_id=agent_id,
            task_id=task_id,
            tree_id=tree_id,
            started_at=datetime.now(),
            max_duration=max_duration,
        )

        session.add_progress_update("session_started", "Work session initiated")
        return session
