"""
Comprehensive Work Session Entity Tests
Tests all aspects of WorkSession domain entity including lifecycle, timing, and status management.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch

from fastmcp.task_management.domain.entities.work_session import WorkSession, SessionStatus
from fastmcp.task_management.domain.value_objects.task_id import TaskId


class TestWorkSessionCreation:
    """Test work session creation and initialization"""
    
    def test_create_session_with_minimal_data(self):
        """Test creating work session with minimal required data"""
        session = WorkSession.create_session(
            agent_id="test_agent",
            task_id="20250625001",
            tree_id="test_tree"
        )
        
        assert session.agent_id == "test_agent"
        assert session.task_id == "20250625001"
        assert session.tree_id == "test_tree"
        assert session.status == SessionStatus.ACTIVE
        assert session.started_at is not None
        assert session.ended_at is None
        assert session.max_duration is None
        assert session.session_notes == ""
        assert len(session.progress_updates) > 0  # Should have initial progress update
        
    def test_create_session_with_all_data(self):
        """Test creating work session with all optional data"""
        session = WorkSession.create_session(
            agent_id="test_agent",
            task_id="20250625001", 
            tree_id="test_tree",
            max_duration_hours=4.0
        )
        
        assert session.agent_id == "test_agent"
        assert session.task_id == "20250625001"
        assert session.tree_id == "test_tree"
        assert session.max_duration is not None
        assert session.max_duration.total_seconds() == 4.0 * 3600  # 4 hours in seconds
        assert session.status == SessionStatus.ACTIVE
        
    def test_create_session_generates_unique_id(self):
        """Test that each session gets a unique ID"""
        session1 = WorkSession.create_session("agent1", "20250625001", "tree1")
        session2 = WorkSession.create_session("agent2", "20250625002", "tree2")
        
        assert session1.id != session2.id
        assert len(session1.id) > 0
        assert len(session2.id) > 0
        
    def test_create_session_sets_created_timestamp(self):
        """Test that session gets proper creation timestamp"""
        before_creation = datetime.now()
        session = WorkSession.create_session("agent", "20250625001", "tree")
        after_creation = datetime.now()
        
        assert before_creation <= session.started_at <= after_creation


class TestWorkSessionStatus:
    """Test work session status management"""
    
    @pytest.fixture
    def active_session(self):
        """Create an active work session for testing"""
        return WorkSession.create_session(
            agent_id="test_agent",
            task_id="20250625001",
            tree_id="test_tree",
            max_duration_hours=2.0
        )
    
    def test_is_active_when_active(self, active_session):
        """Test is_active returns True for active session"""
        assert active_session.is_active() is True
        assert active_session.status == SessionStatus.ACTIVE
        
    def test_is_active_when_paused(self, active_session):
        """Test is_active returns False for paused session"""
        active_session.pause_session("Taking break")
        assert active_session.is_active() is False
        assert active_session.status == SessionStatus.PAUSED
        
    def test_is_active_when_completed(self, active_session):
        """Test is_active returns False for completed session"""
        active_session.complete_session(True, "Task completed successfully")
        assert active_session.is_active() is False
        assert active_session.status == SessionStatus.COMPLETED
        
    def test_is_active_when_cancelled(self, active_session):
        """Test is_active returns False for cancelled session"""
        active_session.cancel_session("Work cancelled due to priority change")
        assert active_session.is_active() is False
        assert active_session.status == SessionStatus.CANCELLED
        
    def test_pause_active_session(self, active_session):
        """Test pausing an active session"""
        active_session.pause_session("Need to take a break")
        
        assert active_session.status == SessionStatus.PAUSED
        assert active_session.is_active() is False
        assert active_session.paused_at is not None
        
    def test_pause_already_paused_session(self, active_session):
        """Test pausing an already paused session"""
        active_session.pause_session("First pause")
        
        with pytest.raises(ValueError, match="Cannot pause session in paused state"):
            active_session.pause_session("Second pause")
        
    def test_pause_completed_session(self, active_session):
        """Test cannot pause a completed session"""
        active_session.complete_session(True, "Work done")
        
        with pytest.raises(ValueError, match="Cannot pause session in completed state"):
            active_session.pause_session("Try to pause")
        
    def test_resume_paused_session(self, active_session):
        """Test resuming a paused session"""
        active_session.pause_session("Temporary pause")
        active_session.resume_session()
        
        assert active_session.status == SessionStatus.ACTIVE
        assert active_session.is_active() is True
        assert active_session.paused_at is None
        
    def test_resume_active_session(self, active_session):
        """Test cannot resume an already active session"""
        with pytest.raises(ValueError, match="Cannot resume session in active state"):
            active_session.resume_session()
        
    def test_resume_completed_session(self, active_session):
        """Test cannot resume a completed session"""
        active_session.complete_session(True, "Work done")
        
        with pytest.raises(ValueError, match="Cannot resume session in completed state"):
            active_session.resume_session()


class TestWorkSessionCompletion:
    """Test work session completion and cancellation"""
    
    @pytest.fixture
    def active_session(self):
        """Create an active work session for testing"""
        return WorkSession.create_session(
            agent_id="test_agent",
            task_id="20250625001",
            tree_id="test_tree"
        )
    
    def test_complete_active_session(self, active_session):
        """Test completing an active session"""
        completion_notes = "Successfully implemented authentication module"
        active_session.complete_session(True, completion_notes)
        
        assert active_session.status == SessionStatus.COMPLETED
        assert completion_notes in active_session.session_notes
        assert active_session.ended_at is not None
        assert active_session.is_active() is False
        
    def test_complete_session_sets_end_timestamp(self, active_session):
        """Test that completion sets proper end timestamp"""
        before_completion = datetime.now()
        active_session.complete_session(True, "Work done")
        after_completion = datetime.now()
        
        assert before_completion <= active_session.ended_at <= after_completion
        
    def test_complete_already_completed_session(self, active_session):
        """Test cannot complete an already completed session"""
        active_session.complete_session(True, "First completion")
        
        with pytest.raises(ValueError, match="Cannot complete session in completed state"):
            active_session.complete_session(True, "Second completion")
        
    def test_complete_cancelled_session(self, active_session):
        """Test cannot complete a cancelled session"""
        active_session.cancel_session("Work cancelled")
        
        with pytest.raises(ValueError, match="Cannot complete session in cancelled state"):
            active_session.complete_session(True, "Trying to complete")
        
    def test_cancel_active_session(self, active_session):
        """Test cancelling an active session"""
        cancellation_reason = "Priority changed, switching to urgent task"
        active_session.cancel_session(cancellation_reason)
        
        assert active_session.status == SessionStatus.CANCELLED
        assert cancellation_reason in active_session.session_notes
        assert active_session.ended_at is not None
        assert active_session.is_active() is False
        
    def test_cancel_paused_session(self, active_session):
        """Test cancelling a paused session"""
        active_session.pause_session("Temporary pause")
        active_session.cancel_session("Cancelling paused work")
        
        assert active_session.status == SessionStatus.CANCELLED
        
    def test_cancel_already_cancelled_session(self, active_session):
        """Test cancelling an already cancelled session overwrites reason"""
        active_session.cancel_session("First cancellation")
        active_session.cancel_session("Second cancellation")
        
        # WorkSession allows multiple cancellations, just updates status again
        assert active_session.status == SessionStatus.CANCELLED
        
    def test_cancel_completed_session(self, active_session):
        """Test cancelling a completed session overwrites status"""
        active_session.complete_session(True, "Work completed")
        active_session.cancel_session("Trying to cancel")
        
        # WorkSession allows cancellation even after completion
        assert active_session.status == SessionStatus.CANCELLED


class TestWorkSessionTiming:
    """Test work session timing and duration management"""
    
    def test_get_duration_active_session(self):
        """Test getting duration of an active session"""
        # Create session with known start time
        session = WorkSession.create_session("agent", "20250625001", "tree")
        session.started_at = datetime.now() - timedelta(hours=2)
        
        duration = session.get_total_duration()
        
        # Should be approximately 2 hours (allow for small timing differences)
        assert timedelta(hours=1.9) <= duration <= timedelta(hours=2.1)
        
    def test_get_duration_completed_session(self):
        """Test getting duration of a completed session"""
        session = WorkSession.create_session("agent", "20250625001", "tree")
        session.started_at = datetime.now() - timedelta(hours=3)
        session.ended_at = datetime.now() - timedelta(hours=1)
        session.status = SessionStatus.COMPLETED
        
        duration = session.get_total_duration()
        
        # Should be exactly 2 hours
        assert timedelta(hours=1.9) <= duration <= timedelta(hours=2.1)
        
    def test_get_elapsed_time_active_session(self):
        """Test getting elapsed time for active session"""
        session = WorkSession.create_session("agent", "20250625001", "tree")
        session.started_at = datetime.now() - timedelta(minutes=30)
        
        elapsed = session.get_active_duration()
        
        # Should be approximately 30 minutes
        assert timedelta(minutes=25) <= elapsed <= timedelta(minutes=35)
        
    def test_get_elapsed_time_completed_session(self):
        """Test getting elapsed time for completed session"""
        session = WorkSession.create_session("agent", "20250625001", "tree")
        session.started_at = datetime.now() - timedelta(hours=2)
        session.ended_at = datetime.now() - timedelta(hours=1)
        session.status = SessionStatus.COMPLETED
        
        elapsed = session.get_active_duration()
        
        # Should use total duration, not time since start
        assert timedelta(hours=0.9) <= elapsed <= timedelta(hours=1.1)
        
    def test_is_timeout_due_no_max_duration(self):
        """Test timeout check when no max duration is set"""
        session = WorkSession.create_session("agent", "20250625001", "tree")
        
        assert session.is_timeout_due() is False
        
    def test_is_timeout_due_within_limit(self):
        """Test timeout check when within time limit"""
        session = WorkSession.create_session(
            "agent", "20250625001", "tree", max_duration_hours=2.0
        )
        session.started_at = datetime.now() - timedelta(hours=1)
        
        assert session.is_timeout_due() is False
        
    def test_is_timeout_due_exceeded_limit(self):
        """Test timeout check when time limit exceeded"""
        session = WorkSession.create_session(
            "agent", "20250625001", "tree", max_duration_hours=1.0
        )
        session.started_at = datetime.now() - timedelta(hours=2)
        
        assert session.is_timeout_due() is True
        
    def test_is_timeout_due_completed_session(self):
        """Test timeout check for completed session"""
        session = WorkSession.create_session(
            "agent", "20250625001", "tree", max_duration_hours=1.0
        )
        session.started_at = datetime.now() - timedelta(hours=2)
        session.complete_session(True, "Work done")
        
        # Completed sessions can still be considered timed out based on duration
        assert session.is_timeout_due() is True
        
    def test_get_remaining_time_no_limit(self):
        """Test getting remaining time when no limit is set"""
        session = WorkSession.create_session("agent", "20250625001", "tree")
        
        # No get_remaining_time method, just check max_duration is None
        assert session.max_duration is None
        
    def test_get_remaining_time_within_limit(self):
        """Test calculating remaining time when within limit"""
        session = WorkSession.create_session(
            "agent", "20250625001", "tree", max_duration_hours=2.0
        )
        session.started_at = datetime.now() - timedelta(hours=0.5)
        
        # Calculate remaining time manually
        elapsed = session.get_total_duration()
        remaining = session.max_duration - elapsed
        
        # Should have approximately 1.5 hours remaining
        assert timedelta(hours=1.4) <= remaining <= timedelta(hours=1.6)
        
    def test_get_remaining_time_exceeded_limit(self):
        """Test calculating remaining time when limit exceeded"""
        session = WorkSession.create_session(
            "agent", "20250625001", "tree", max_duration_hours=1.0
        )
        session.started_at = datetime.now() - timedelta(hours=2)
        
        # Calculate remaining time manually
        elapsed = session.get_total_duration()
        remaining = session.max_duration - elapsed
        
        # Should be negative (overtime)
        assert remaining < timedelta(0)
        assert timedelta(hours=-1.1) <= remaining <= timedelta(hours=-0.9)


class TestWorkSessionProgress:
    """Test work session progress tracking"""
    
    @pytest.fixture
    def session_with_progress(self):
        """Create a session for progress testing"""
        return WorkSession.create_session(
            agent_id="test_agent",
            task_id="20250625001",
            tree_id="test_tree"
        )
    
    def test_add_progress_update(self, session_with_progress):
        """Test adding progress updates"""
        initial_count = len(session_with_progress.progress_updates)
        session_with_progress.add_progress_update("task_started", "Started working on authentication")
        
        assert len(session_with_progress.progress_updates) == initial_count + 1
        latest_update = session_with_progress.progress_updates[-1]
        assert latest_update["type"] == "task_started"
        assert latest_update["message"] == "Started working on authentication"
        
    def test_add_progress_update_with_metadata(self, session_with_progress):
        """Test adding progress update with metadata"""
        metadata = {"component": "auth_module", "lines_of_code": 150}
        session_with_progress.add_progress_update("code_written", "Implemented JWT validation", metadata)
        
        latest_update = session_with_progress.progress_updates[-1]
        assert latest_update["metadata"] == metadata
        
    def test_lock_resource(self, session_with_progress):
        """Test locking a resource"""
        resource_id = "database_connection_1"
        session_with_progress.lock_resource(resource_id)
        
        assert resource_id in session_with_progress.resources_locked
        # Should add progress update about resource lock
        progress_messages = [u["message"] for u in session_with_progress.progress_updates]
        assert any("Locked resource" in msg for msg in progress_messages)
        
    def test_unlock_resource(self, session_with_progress):
        """Test unlocking a resource"""
        resource_id = "database_connection_1"
        session_with_progress.lock_resource(resource_id)
        session_with_progress.unlock_resource(resource_id)
        
        assert resource_id not in session_with_progress.resources_locked
        
    def test_unlock_all_resources(self, session_with_progress):
        """Test unlocking all resources"""
        resources = ["db_conn_1", "file_handle_1", "api_key_1"]
        for resource in resources:
            session_with_progress.lock_resource(resource)
        
        session_with_progress.unlock_all_resources()
        
        assert len(session_with_progress.resources_locked) == 0
        
    def test_extend_session(self, session_with_progress):
        """Test extending session duration"""
        additional_hours = timedelta(hours=2)
        session_with_progress.extend_session(additional_hours)
        
        assert session_with_progress.max_duration == additional_hours
        # Should add progress update about extension
        progress_messages = [u["message"] for u in session_with_progress.progress_updates]
        assert any("extended" in msg.lower() for msg in progress_messages)
        
    def test_add_notes_to_active_session(self, session_with_progress):
        """Test adding notes to active session"""
        initial_notes = "Started authentication work"
        session_with_progress.session_notes = initial_notes
        
        additional_notes = "\nImplemented JWT token validation"
        session_with_progress.session_notes += additional_notes
        
        expected = initial_notes + additional_notes
        assert session_with_progress.session_notes == expected
        
    def test_add_notes_to_empty_session(self, session_with_progress):
        """Test adding notes to session with no existing notes"""
        notes = "Starting implementation of user authentication"
        session_with_progress.session_notes = notes
        
        assert session_with_progress.session_notes == notes
        
    def test_update_activity(self, session_with_progress):
        """Test updating last activity timestamp"""
        original_activity = session_with_progress.last_activity
        import time
        time.sleep(0.01)  # Small delay
        session_with_progress.update_activity()
        
        assert session_with_progress.last_activity > original_activity


class TestWorkSessionSummary:
    """Test work session summary generation"""
    
    def test_get_session_summary_active_session(self):
        """Test getting summary for active session"""
        session = WorkSession.create_session(
            agent_id="frontend_agent",
            task_id="20250625001",
            tree_id="ui_development",
            max_duration_hours=4.0
        )
        session.session_notes = "Working on React components"
        session.started_at = datetime.now() - timedelta(hours=2)
        
        summary = session.get_session_summary()
        
        assert summary["session_id"] == session.id
        assert summary["agent_id"] == "frontend_agent"
        assert summary["task_id"] == "20250625001"
        assert summary["tree_id"] == "ui_development"
        assert summary["status"] == "active"
        assert summary["progress"]["session_notes"] == "Working on React components"
        assert summary["configuration"]["max_duration"] is not None
        assert summary["timing"]["started_at"] is not None
        assert summary["timing"]["ended_at"] is None
        assert summary["configuration"]["timeout_due"] is False
        
    def test_get_session_summary_completed_session(self):
        """Test getting summary for completed session"""
        session = WorkSession.create_session(
            "backend_agent", "20250625002", "api_development"
        )
        session.started_at = datetime.now() - timedelta(hours=3)
        session.complete_session(True, "API endpoints implemented successfully")
        
        summary = session.get_session_summary()
        
        assert summary["status"] == "completed"
        assert "API endpoints implemented successfully" in summary["progress"]["session_notes"]
        assert summary["timing"]["ended_at"] is not None
        
    def test_get_session_summary_paused_session(self):
        """Test getting summary for paused session"""
        session = WorkSession.create_session(
            "qa_agent", "20250625003", "testing"
        )
        session.pause_session("Taking a break")
        
        summary = session.get_session_summary()
        
        assert summary["status"] == "paused"
        assert summary["timing"]["paused_at"] is not None
        
    def test_get_session_summary_with_timeout(self):
        """Test getting summary for session that exceeded timeout"""
        session = WorkSession.create_session(
            "devops_agent", "20250625004", "deployment", max_duration_hours=1.0
        )
        session.started_at = datetime.now() - timedelta(hours=2)
        
        summary = session.get_session_summary()
        
        assert summary["configuration"]["timeout_due"] is True


class TestWorkSessionEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_create_session_with_empty_agent_id(self):
        """Test creating session with empty agent ID"""
        # WorkSession.create_session doesn't validate empty strings, just test it creates session
        session = WorkSession.create_session("", "20250625001", "tree")
        assert session.agent_id == ""
            
    def test_create_session_with_empty_task_id(self):
        """Test creating session with empty task ID"""
        session = WorkSession.create_session("agent", "", "tree")
        assert session.task_id == ""
            
    def test_create_session_with_empty_tree_id(self):
        """Test creating session with empty tree ID"""
        session = WorkSession.create_session("agent", "20250625001", "")
        assert session.tree_id == ""
            
    def test_create_session_with_negative_duration(self):
        """Test creating session with negative max duration"""
        # WorkSession.create_session allows negative duration
        session = WorkSession.create_session(
            "agent", "20250625001", "tree", max_duration_hours=-1.0
        )
        assert session.max_duration.total_seconds() < 0
            
    def test_create_session_with_zero_duration(self):
        """Test creating session with zero max duration"""
        session = WorkSession.create_session(
            "agent", "20250625001", "tree", max_duration_hours=0.0
        )
        # Zero duration creates None max_duration
        assert session.max_duration is None or session.max_duration.total_seconds() == 0
            
    def test_session_state_transitions(self):
        """Test various state transitions"""
        session = WorkSession.create_session("agent", "20250625001", "tree")
        
        # Active -> Paused -> Active
        session.pause_session("Taking break")
        assert session.status == SessionStatus.PAUSED
        session.resume_session()
        assert session.status == SessionStatus.ACTIVE
        
        # Active -> Completed
        session.complete_session(True, "Done")
        assert session.status == SessionStatus.COMPLETED
        
    def test_session_timing_edge_cases(self):
        """Test timing calculations with edge cases"""
        session = WorkSession.create_session("agent", "20250625001", "tree")
        
        # Very recent session (should have near-zero duration)
        duration = session.get_total_duration()
        assert duration >= timedelta(0)
        assert duration < timedelta(seconds=1)  # Less than 1 second
        
        # Session with exactly matching start and end times
        now = datetime.now()
        session.started_at = now
        session.ended_at = now
        session.status = SessionStatus.COMPLETED
        
        duration = session.get_total_duration()
        assert duration == timedelta(0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])