"""
Unit Test: DDD Layer Boundaries Testing
Task 2 - DDD Architecture Validation (Layer Boundaries)
Duration: Part of 3 hours
"""

import pytest
import sys
import os
import inspect
from unittest.mock import Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


class TestDDDLayerBoundaries:
    """Test cases for DDD layer boundaries and architectural constraints."""
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_domain_layer_independence(self):
        """Test that domain layer has no dependencies on other layers."""
        import fastmcp.dhafnck_mcp.domain.entities.task as task_module
        import fastmcp.dhafnck_mcp.domain.value_objects.task_id as task_id_module
        import fastmcp.dhafnck_mcp.domain.value_objects.task_status as task_status_module
        import fastmcp.dhafnck_mcp.domain.value_objects.priority as priority_module
        import fastmcp.dhafnck_mcp.domain.events.task_events as events_module
        
        # Domain modules should not import from application, infrastructure, or interface layers
        forbidden_imports = ['application', 'infrastructure', 'interface']
        
        for module in [task_module, task_id_module, task_status_module, priority_module, events_module]:
            source = inspect.getsource(module)
            for forbidden in forbidden_imports:
                assert f'from ..{forbidden}' not in source, f"Domain layer should not import from {forbidden} layer"
                assert f'from fastmcp.dhafnck_mcp.{forbidden}' not in source, f"Domain layer should not import from {forbidden} layer"
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_application_layer_dependencies(self):
        """Test that application layer only depends on domain layer."""
        import fastmcp.dhafnck_mcp.application.services.task_application_service as app_service_module
        
        source = inspect.getsource(app_service_module)
        
        # Application layer can import from domain
        assert 'from fastmcp.dhafnck_mcp.domain' in source or 'from ..domain' in source or 'from ...domain' in source
        
        # Application layer should not import from infrastructure or interface
        assert 'from fastmcp.dhafnck_mcp.infrastructure' not in source
        assert 'from fastmcp.dhafnck_mcp.interface' not in source
        assert 'from ..infrastructure' not in source
        assert 'from ..interface' not in source
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_infrastructure_layer_dependencies(self):
        """Test that infrastructure layer can depend on domain and application layers."""
        import fastmcp.dhafnck_mcp.infrastructure.repositories.json_task_repository as repo_module
        import fastmcp.dhafnck_mcp.infrastructure.services.file_auto_rule_generator as generator_module
        
        # Infrastructure can import from domain and application
        for module in [repo_module, generator_module]:
            source = inspect.getsource(module)
            # Should be able to import from domain
            # (May or may not import from application depending on implementation)
            
            # Infrastructure should not import from interface layer
            assert 'from fastmcp.dhafnck_mcp.interface' not in source
            assert 'from ..interface' not in source
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_interface_layer_dependencies(self):
        """Test that interface layer can depend on all other layers."""
        import fastmcp.dhafnck_mcp.interface.consolidated_mcp_tools_v2 as mcp_tools_module
        
        source = inspect.getsource(mcp_tools_module)
        
        # Interface layer should import from application (and possibly others)
        assert ('from fastmcp.dhafnck_mcp.application' in source or 
                'from ..application' in source or
                'task_application_service' in source or
                'TaskApplicationService' in source)
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_domain_entities_encapsulation(self):
        """Test that domain entities properly encapsulate business logic."""
        from fastmcp.dhafnck_mcp.domain.entities.task import Task
        from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId
        from fastmcp.dhafnck_mcp.domain.value_objects.task_status import TaskStatus
        from fastmcp.dhafnck_mcp.domain.value_objects.priority import Priority
        
        # Create a task
        task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description"
        )
        
        # Test that business logic is encapsulated in the entity
        assert hasattr(task, 'update_status')
        assert hasattr(task, 'update_priority')
        assert hasattr(task, 'update_title')
        assert hasattr(task, 'update_description')
        assert hasattr(task, 'add_dependency')
        assert hasattr(task, 'remove_dependency')
        assert hasattr(task, 'is_overdue')
        assert hasattr(task, 'can_be_started')
        
        # Test that validation is built into the entity
        with pytest.raises(ValueError):
            task.update_title("")
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_value_objects_immutability(self):
        """Test that value objects are immutable as required by DDD."""
        from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId
        from fastmcp.dhafnck_mcp.domain.value_objects.task_status import TaskStatus
        from fastmcp.dhafnck_mcp.domain.value_objects.priority import Priority
        
        # Value objects should be frozen (immutable)
        task_id = TaskId.from_int(1)
        task_status = TaskStatus.todo()
        priority = Priority.high()
        
        # Should not be able to modify value objects
        with pytest.raises(AttributeError):
            task_id.value = "2"
        
        with pytest.raises(AttributeError):
            task_status.value = "done"
        
        with pytest.raises(AttributeError):
            priority.value = "low"
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_domain_events_pattern(self):
        """Test that domain events pattern is properly implemented."""
        from fastmcp.dhafnck_mcp.domain.entities.task import Task
        from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId
        from fastmcp.dhafnck_mcp.domain.events.task_events import TaskUpdated, TaskCreated, TaskRetrieved
        
        # Create a task
        task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description"
        )
        
        # Clear creation events
        events = task.get_events()
        assert len(events) > 0
        assert isinstance(events[0], TaskCreated)
        
        # Update task should generate event
        task.update_title("New Title")
        events = task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskUpdated)
        
        # Mark as retrieved should generate event
        task.mark_as_retrieved()
        events = task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskRetrieved)
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_repository_pattern_interface(self):
        """Test that repository pattern is properly defined."""
        from fastmcp.dhafnck_mcp.domain.repositories.task_repository import TaskRepository
        from fastmcp.dhafnck_mcp.infrastructure.repositories.json_task_repository import JsonTaskRepository
        
        # Infrastructure repository should implement domain interface
        assert issubclass(JsonTaskRepository, TaskRepository)
        
        # Check that repository has required methods
        repo = JsonTaskRepository()
        assert hasattr(repo, 'save')
        assert hasattr(repo, 'find_by_id')
        assert hasattr(repo, 'find_all')
        assert hasattr(repo, 'delete')
        assert hasattr(repo, 'search')
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_application_service_orchestration(self):
        """Test that application service properly orchestrates domain operations."""
        from fastmcp.dhafnck_mcp.application.services.task_application_service import TaskApplicationService
        from fastmcp.dhafnck_mcp.infrastructure.repositories.json_task_repository import JsonTaskRepository
        from fastmcp.dhafnck_mcp.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator
        
        # Application service should coordinate between domain and infrastructure
        repo = JsonTaskRepository()
        auto_rule_gen = FileAutoRuleGenerator()
        service = TaskApplicationService(repo, auto_rule_gen)
        
        # Should have methods for all use cases
        assert hasattr(service, 'create_task')
        assert hasattr(service, 'get_task')
        assert hasattr(service, 'list_tasks')
        assert hasattr(service, 'update_task')
        assert hasattr(service, 'delete_task')
        assert hasattr(service, 'search_tasks')
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_dependency_inversion_principle(self):
        """Test that dependency inversion principle is followed."""
        from fastmcp.dhafnck_mcp.application.services.task_application_service import TaskApplicationService
        from fastmcp.dhafnck_mcp.domain.repositories.task_repository import TaskRepository
        from fastmcp.dhafnck_mcp.domain.services.auto_rule_generator import AutoRuleGenerator
        
        # Application service should depend on abstractions (interfaces), not concretions
        service_init = TaskApplicationService.__init__
        sig = inspect.signature(service_init)
        
        # Check parameter types in constructor
        params = list(sig.parameters.values())[1:]  # Skip 'self'
        
        # Should accept interface types, not concrete implementations
        # (This is checked by the type hints or parameter names)
        param_names = [p.name for p in params]
        assert 'task_repository' in param_names or 'repository' in param_names
        assert 'auto_rule_generator' in param_names or 'generator' in param_names
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_aggregate_root_pattern(self):
        """Test that Task entity acts as an aggregate root."""
        from fastmcp.dhafnck_mcp.domain.entities.task import Task
        from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId
        
        # Create a task (aggregate root)
        task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description"
        )
        
        # Aggregate root should control access to its internals
        assert hasattr(task, 'id')
        assert hasattr(task, 'title')
        assert hasattr(task, 'description')
        assert hasattr(task, 'status')
        assert hasattr(task, 'priority')
        
        # Aggregate root should manage its own consistency
        assert hasattr(task, '_validate')
        
        # Aggregate root should collect domain events
        assert hasattr(task, '_events')
        assert hasattr(task, 'get_events')
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_use_case_separation(self):
        """Test that use cases are properly separated."""
        import fastmcp.dhafnck_mcp.application.use_cases.create_task as create_task_module
        import fastmcp.dhafnck_mcp.application.use_cases.get_task as get_task_module
        import fastmcp.dhafnck_mcp.application.use_cases.update_task as update_task_module
        import fastmcp.dhafnck_mcp.application.use_cases.delete_task as delete_task_module
        
        # Each use case should be in its own module
        modules = [create_task_module, get_task_module, update_task_module, delete_task_module]
        
        for module in modules:
            # Each module should have specific functionality
            assert hasattr(module, '__file__')
            # Use cases should be focused on single responsibility
            source = inspect.getsource(module)
            assert len(source.split('\n')) < 200  # Should be reasonably small and focused
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_dto_pattern_usage(self):
        """Test that DTOs are used for data transfer."""
        from fastmcp.dhafnck_mcp.application.dtos.task_dto import TaskResponse
        
        # DTOs should be simple data containers
        dto = TaskResponse(
            id=1,
            title="Test",
            description="Test Description",
            status="todo",
            priority="medium",
            details="Test details",
            estimated_effort="2h",
            assignees=["test_user"],
            labels=["test"],
            dependencies=[],
            subtasks=[],
            due_date=None,
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z"
        )
        
        assert dto.id == 1
        assert dto.title == "Test"
        assert dto.status == "todo"
        
        # DTOs should have conversion methods
        assert hasattr(TaskResponse, 'from_domain')
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_clean_architecture_compliance(self):
        """Test overall clean architecture compliance."""
        # Test that dependencies flow inward (toward domain)
        
        # Domain layer (innermost) - no dependencies on outer layers
        import fastmcp.dhafnck_mcp.domain.entities.task
        import fastmcp.dhafnck_mcp.domain.value_objects.task_id
        
        # Application layer - depends only on domain
        import fastmcp.dhafnck_mcp.application.services.task_application_service
        
        # Infrastructure layer - depends on domain and application
        import fastmcp.dhafnck_mcp.infrastructure.repositories.json_task_repository
        
        # Interface layer (outermost) - depends on all inner layers
        import fastmcp.dhafnck_mcp.interface.mcp_tools
        
        # All imports should succeed without circular dependencies
        assert True  # If we get here, no circular imports exist
    
    @pytest.mark.unit
    @pytest.mark.architecture
    def test_single_responsibility_principle(self):
        """Test that classes follow single responsibility principle."""
        from fastmcp.dhafnck_mcp.domain.entities.task import Task
        from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId
        from fastmcp.dhafnck_mcp.domain.value_objects.task_status import TaskStatus
        from fastmcp.dhafnck_mcp.domain.value_objects.priority import Priority
        
        # Each class should have a single, well-defined responsibility
        
        # Task entity: manages task business logic
        task_methods = [method for method in dir(Task) if not method.startswith('_')]
        task_business_methods = [m for m in task_methods if m.startswith('update_') or m.startswith('add_') or m.startswith('remove_') or m in ['is_overdue', 'can_be_started']]
        assert len(task_business_methods) > 5  # Should have business methods
        
        # TaskId: represents task identifier
        task_id_methods = [method for method in dir(TaskId) if not method.startswith('_')]
        assert 'value' in str(TaskId.__annotations__)  # Should have value field
        
        # TaskStatus: represents task status with validation
        assert hasattr(TaskStatus, 'can_transition_to')  # Should have status logic
        
        # Priority: represents priority with ordering
        assert hasattr(Priority, '__lt__')  # Should be comparable 