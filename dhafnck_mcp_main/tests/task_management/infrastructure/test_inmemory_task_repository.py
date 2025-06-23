"""
This is the canonical and only maintained test suite for InMemoryTaskRepository.
All CRUD, search, and statistics tests should be added here.
"""

import pytest
from fastmcp.task_management.infrastructure.repositories.json_task_repository import InMemoryTaskRepository
from fastmcp.task_management.domain import Task, TaskId, TaskStatus, Priority

class TestInMemoryTaskRepository:
    @pytest.fixture
    def repository(self):
        return InMemoryTaskRepository()

    @pytest.fixture
    def sample_task(self):
        return Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description",
            priority=Priority.high(),
            assignees=["user1"],
            labels=["label1"]
        )

    def test_save_and_find_by_id(self, repository, sample_task):
        repository.save(sample_task)
        found = repository.find_by_id(sample_task.id)
        assert found is not None
        assert found.id == sample_task.id
        assert found.title == sample_task.title

    def test_find_all(self, repository, sample_task):
        assert repository.find_all() == []
        repository.save(sample_task)
        all_tasks = repository.find_all()
        assert len(all_tasks) == 1
        assert all_tasks[0].id == sample_task.id

    def test_delete(self, repository, sample_task):
        repository.save(sample_task)
        assert repository.exists(sample_task.id)
        result = repository.delete(sample_task.id)
        assert result is True
        assert not repository.exists(sample_task.id)
        # Delete non-existent
        result = repository.delete(TaskId.from_int(999))
        assert result is False

    def test_get_next_id(self, repository):
        id1 = repository.get_next_id()
        id2 = repository.get_next_id()
        assert id1 != id2
        assert isinstance(id1, TaskId)
        assert isinstance(id2, TaskId)

    def test_find_by_criteria(self, repository, sample_task):
        repository.save(sample_task)
        results = repository.find_by_criteria({"priority": Priority.high()})
        assert len(results) == 1
        assert results[0].id == sample_task.id

    def test_search(self, repository, sample_task):
        repository.save(sample_task)
        results = repository.search("Test Task")
        assert len(results) == 1
        assert results[0].id == sample_task.id
        results = repository.search("nonexistent")
        assert results == []

    def test_statistics(self, repository, sample_task):
        stats = repository.get_statistics()
        assert stats["total_tasks"] == 0
        repository.save(sample_task)
        stats = repository.get_statistics()
        assert stats["total_tasks"] == 1
        assert stats["priority_distribution"]["high"] == 1 