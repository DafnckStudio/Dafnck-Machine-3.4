"""
Comprehensive Dependency Management and Resolution Tests
Tests dependency algorithms, cycle detection, and cross-tree coordination.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from typing import Dict, List, Set

# Import domain entities and services
from fastmcp.task_management.domain.entities.project import Project
from fastmcp.task_management.domain.entities.task_tree import TaskTree
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
from fastmcp.task_management.domain.value_objects.priority import Priority


class TestDependencyManagement:
    """Test dependency management and resolution algorithms"""
    
    @pytest.fixture
    def complex_project(self):
        """Create a complex project with multiple trees and interdependencies"""
        now = datetime.now(timezone.utc)
        
        project = Project(
            id="complex_project",
            name="Complex Multi-Service Application",
            description="Microservices architecture with complex dependencies",
            created_at=now,
            updated_at=now
        )
        
        # Create multiple service trees
        trees = {
            "auth_service": TaskTree(
                id="auth_service",
                name="Authentication Service",
                description="User authentication and authorization",
                project_id="complex_project",
                created_at=now
            ),
            "user_service": TaskTree(
                id="user_service",
                name="User Management Service",
                description="User profile and data management",
                project_id="complex_project",
                created_at=now
            ),
            "product_service": TaskTree(
                id="product_service",
                name="Product Catalog Service",
                description="Product inventory and catalog management",
                project_id="complex_project",
                created_at=now
            ),
            "order_service": TaskTree(
                id="order_service",
                name="Order Processing Service",
                description="Order management and processing",
                project_id="complex_project",
                created_at=now
            ),
            "payment_service": TaskTree(
                id="payment_service",
                name="Payment Processing Service",
                description="Payment gateway and transaction processing",
                project_id="complex_project",
                created_at=now
            ),
            "notification_service": TaskTree(
                id="notification_service",
                name="Notification Service",
                description="Email and SMS notifications",
                project_id="complex_project",
                created_at=now
            )
        }
        
        # Add trees to project
        for tree_id, tree in trees.items():
            project.task_trees[tree_id] = tree
        
        return project, trees
    
    @pytest.fixture
    def dependency_tasks(self, complex_project):
        """Create tasks with complex dependency relationships"""
        project, trees = complex_project
        
        # Authentication Service Tasks
        auth_tasks = [
            Task.create(
                id=TaskId.from_string("20250625101"),
                title="JWT Token Implementation",
                description="Implement JWT-based authentication",
                status=TaskStatus("todo"),
                priority=Priority("high")
            ),
            Task.create(
                id=TaskId.from_string("20250625102"),
                title="OAuth Integration",
                description="Integrate with OAuth providers",
                status=TaskStatus("todo"),
                priority=Priority("medium")
            ),
            Task.create(
                id=TaskId.from_string("20250625103"),
                title="Auth API Endpoints",
                description="Create authentication API endpoints",
                status=TaskStatus("todo"),
                priority=Priority("high")
            )
        ]
        
        # User Service Tasks
        user_tasks = [
            Task.create(
                id=TaskId.from_string("20250625201"),
                title="User Profile Schema",
                description="Design user profile database schema",
                status=TaskStatus("todo"),
                priority=Priority("high")
            ),
            Task.create(
                id=TaskId.from_string("20250625202"),
                title="User CRUD Operations",
                description="Implement user create/read/update/delete",
                status=TaskStatus("todo"),
                priority=Priority("high")
            ),
            Task.create(
                id=TaskId.from_string("20250625203"),
                title="User Profile API",
                description="Create user profile management API",
                status=TaskStatus("todo"),
                priority=Priority("medium")
            )
        ]
        
        # Product Service Tasks
        product_tasks = [
            Task.create(
                id=TaskId.from_string("20250625301"),
                title="Product Database Schema",
                description="Design product catalog database",
                status=TaskStatus("todo"),
                priority=Priority("high")
            ),
            Task.create(
                id=TaskId.from_string("20250625302"),
                title="Product Search Engine",
                description="Implement product search functionality",
                status=TaskStatus("todo"),
                priority=Priority("medium")
            ),
            Task.create(
                id=TaskId.from_string("20250625303"),
                title="Inventory Management",
                description="Implement inventory tracking system",
                status=TaskStatus("todo"),
                priority=Priority("high")
            )
        ]
        
        # Order Service Tasks
        order_tasks = [
            Task.create(
                id=TaskId.from_string("20250625401"),
                title="Order Processing Engine",
                description="Core order processing logic",
                status=TaskStatus("todo"),
                priority=Priority("critical")
            ),
            Task.create(
                id=TaskId.from_string("20250625402"),
                title="Order State Management",
                description="Implement order state machine",
                status=TaskStatus("todo"),
                priority=Priority("high")
            ),
            Task.create(
                id=TaskId.from_string("20250625403"),
                title="Order History API",
                description="Create order history and tracking API",
                status=TaskStatus("todo"),
                priority=Priority("medium")
            )
        ]
        
        # Payment Service Tasks
        payment_tasks = [
            Task.create(
                id=TaskId.from_string("20250625501"),
                title="Payment Gateway Integration",
                description="Integrate with payment processors",
                status=TaskStatus("todo"),
                priority=Priority("critical")
            ),
            Task.create(
                id=TaskId.from_string("20250625502"),
                title="Transaction Security",
                description="Implement secure transaction handling",
                status=TaskStatus("todo"),
                priority=Priority("critical")
            ),
            Task.create(
                id=TaskId.from_string("20250625503"),
                title="Payment Status Tracking",
                description="Implement payment status monitoring",
                status=TaskStatus("todo"),
                priority=Priority("high")
            )
        ]
        
        # Notification Service Tasks
        notification_tasks = [
            Task.create(
                id=TaskId.from_string("20250625601"),
                title="Email Service Integration",
                description="Integrate with email service provider",
                status=TaskStatus("todo"),
                priority=Priority("medium")
            ),
            Task.create(
                id=TaskId.from_string("20250625602"),
                title="SMS Service Integration",
                description="Integrate with SMS service provider",
                status=TaskStatus("todo"),
                priority=Priority("medium")
            ),
            Task.create(
                id=TaskId.from_string("20250625603"),
                title="Notification Templates",
                description="Create notification template system",
                status=TaskStatus("todo"),
                priority=Priority("low")
            )
        ]
        
        # Add tasks to trees
        for task in auth_tasks:
            trees["auth_service"].add_root_task(task)
        for task in user_tasks:
            trees["user_service"].add_root_task(task)
        for task in product_tasks:
            trees["product_service"].add_root_task(task)
        for task in order_tasks:
            trees["order_service"].add_root_task(task)
        for task in payment_tasks:
            trees["payment_service"].add_root_task(task)
        for task in notification_tasks:
            trees["notification_service"].add_root_task(task)
        
        return {
            "auth": auth_tasks,
            "user": user_tasks,
            "product": product_tasks,
            "order": order_tasks,
            "payment": payment_tasks,
            "notification": notification_tasks
        }
    
    @pytest.mark.integration
    def test_linear_dependency_chain(self, complex_project, dependency_tasks):
        """Test linear dependency chain resolution"""
        project, trees = complex_project
        
        # Create linear dependency chain: Auth → User → Product → Order → Payment → Notification
        project.add_cross_tree_dependency("20250625201", "20250625103")  # User Profile depends on Auth API
        project.add_cross_tree_dependency("20250625301", "20250625202")  # Product Schema depends on User CRUD
        project.add_cross_tree_dependency("20250625401", "20250625303")  # Order Processing depends on Inventory
        project.add_cross_tree_dependency("20250625501", "20250625401")  # Payment Gateway depends on Order Processing
        project.add_cross_tree_dependency("20250625601", "20250625503")  # Email Service depends on Payment Status
        
        # Verify dependencies are established
        assert "20250625201" in project.cross_tree_dependencies
        assert "20250625301" in project.cross_tree_dependencies
        assert "20250625401" in project.cross_tree_dependencies
        assert "20250625501" in project.cross_tree_dependencies
        assert "20250625601" in project.cross_tree_dependencies
        
        # Test dependency coordination
        coordination_result = project.coordinate_cross_tree_dependencies()
        
        # All tasks should be blocked initially since no prerequisites are complete
        assert coordination_result["total_dependencies"] == 5
        blocked_tasks = coordination_result["blocked_tasks"]
        ready_tasks = coordination_result["ready_tasks"]
        
        # Initially, all dependent tasks should be blocked
        assert len(blocked_tasks) >= 4  # At least 4 tasks are blocked by dependencies
        
        # Complete tasks one by one and verify dependency resolution
        # Complete Auth API (20250625103)
        auth_api_task = None
        for task in dependency_tasks["auth"]:
            if task.id.value == "20250625103":
                auth_api_task = task
                break
        
        if auth_api_task:
            auth_api_task.status = TaskStatus("done")
            coordination_result = project.coordinate_cross_tree_dependencies()
            assert "20250625201" in coordination_result["ready_tasks"]  # User Profile should be ready
    
    @pytest.mark.integration
    def test_complex_dependency_graph(self, complex_project, dependency_tasks):
        """Test complex dependency graph with multiple paths"""
        project, trees = complex_project
        
        # Create complex dependency graph:
        # Order Processing depends on both User CRUD and Product Schema
        project.add_cross_tree_dependency("20250625401", "20250625202")  # Order → User CRUD
        project.add_cross_tree_dependency("20250625401", "20250625301")  # Order → Product Schema
        
        # Payment Gateway depends on both Order Processing and Auth API
        project.add_cross_tree_dependency("20250625501", "20250625401")  # Payment → Order
        project.add_cross_tree_dependency("20250625501", "20250625103")  # Payment → Auth API
        
        # Notification depends on Payment Status and User Profile API
        project.add_cross_tree_dependency("20250625601", "20250625503")  # Notification → Payment Status
        project.add_cross_tree_dependency("20250625601", "20250625203")  # Notification → User Profile API
        
        # Test that Order Processing is blocked until both dependencies are met
        coordination_result = project.coordinate_cross_tree_dependencies()
        assert "20250625401" in coordination_result["blocked_tasks"]
        
        # Complete User CRUD but not Product Schema
        user_crud_task = None
        for task in dependency_tasks["user"]:
            if task.id.value == "20250625202":
                user_crud_task = task
                break
        
        if user_crud_task:
            user_crud_task.status = TaskStatus("done")
            coordination_result = project.coordinate_cross_tree_dependencies()
            # Order Processing should still be blocked (needs Product Schema too)
            assert "20250625401" in coordination_result["blocked_tasks"]
        
        # Complete Product Schema
        product_schema_task = None
        for task in dependency_tasks["product"]:
            if task.id.value == "20250625301":
                product_schema_task = task
                break
        
        if product_schema_task:
            product_schema_task.status = TaskStatus("done")
            coordination_result = project.coordinate_cross_tree_dependencies()
            # Now Order Processing should be ready
            assert "20250625401" in coordination_result["ready_tasks"]
    
    @pytest.mark.integration
    def test_dependency_cycle_detection(self, complex_project, dependency_tasks):
        """Test detection and handling of dependency cycles"""
        project, trees = complex_project
        
        # Create a dependency cycle: A → B → C → A
        project.add_cross_tree_dependency("20250625202", "20250625301")  # User CRUD → Product Schema
        project.add_cross_tree_dependency("20250625301", "20250625401")  # Product Schema → Order Processing
        
        # Attempt to create cycle: Order Processing → User CRUD (this would complete the cycle)
        try:
            project.add_cross_tree_dependency("20250625401", "20250625202")
            # The system should detect the cycle
            coordination_result = project.coordinate_cross_tree_dependencies()
            
            # All tasks in the cycle should be identified as problematic
            assert coordination_result["total_dependencies"] == 3
            # Tasks involved in cycle should be in blocked_tasks since they form a cycle
            blocked_tasks = coordination_result["blocked_tasks"]
            assert "20250625202" in blocked_tasks
            assert "20250625301" in blocked_tasks
            assert "20250625401" in blocked_tasks
            
        except Exception as e:
            # Alternatively, the system might prevent cycle creation entirely
            assert "cycle" in str(e).lower() or "circular" in str(e).lower()
    
    @pytest.mark.integration
    def test_dependency_resolution_priority(self, complex_project, dependency_tasks):
        """Test dependency resolution respects task priorities"""
        project, trees = complex_project
        
        # Create dependencies where high-priority tasks depend on lower-priority ones
        project.add_cross_tree_dependency("20250625401", "20250625603")  # Critical Order → Low Notification Templates
        project.add_cross_tree_dependency("20250625501", "20250625602")  # Critical Payment → Medium SMS Service
        
        coordination_result = project.coordinate_cross_tree_dependencies()
        
        # Verify that high-priority tasks are blocked by lower-priority dependencies
        assert "20250625401" in coordination_result["blocked_tasks"]
        assert "20250625501" in coordination_result["blocked_tasks"]
        
        # This tests the system's ability to handle priority inversions
        # High-priority tasks blocked by low-priority dependencies should be flagged
        
        # Complete low-priority dependency
        notification_template_task = None
        for task in dependency_tasks["notification"]:
            if task.id.value == "20250625603":
                notification_template_task = task
                break
        
        if notification_template_task:
            notification_template_task.status = TaskStatus("done")
            coordination_result = project.coordinate_cross_tree_dependencies()
            assert "20250625401" in coordination_result["ready_tasks"]
    
    @pytest.mark.integration
    def test_cross_tree_dependency_impact_analysis(self, complex_project, dependency_tasks):
        """Test analysis of dependency impact across trees"""
        project, trees = complex_project
        
        # Create dependencies that span multiple trees
        project.add_cross_tree_dependency("20250625401", "20250625103")  # Order → Auth
        project.add_cross_tree_dependency("20250625401", "20250625202")  # Order → User
        project.add_cross_tree_dependency("20250625401", "20250625301")  # Order → Product
        project.add_cross_tree_dependency("20250625501", "20250625401")  # Payment → Order
        project.add_cross_tree_dependency("20250625502", "20250625401")  # Transaction Security → Order
        project.add_cross_tree_dependency("20250625601", "20250625501")  # Notification → Payment
        
        # Analyze impact of Order Processing task
        coordination_result = project.coordinate_cross_tree_dependencies()
        
        # Order Processing has 3 dependencies (blocks 3 other services)
        order_dependent_tasks = []
        for dependent_task, prerequisites in project.cross_tree_dependencies.items():
            if "20250625401" in prerequisites:
                order_dependent_tasks.append(dependent_task)
        
        # Payment service tasks depend on Order Processing
        assert "20250625501" in order_dependent_tasks  # Payment Gateway
        assert "20250625502" in order_dependent_tasks  # Transaction Security
        
        # Verify cascade effect: if Order Processing is delayed, it affects multiple downstream services
        assert len(order_dependent_tasks) >= 2
    
    @pytest.mark.integration
    def test_dependency_resolution_performance(self, complex_project, dependency_tasks):
        """Test dependency resolution performance with large dependency graphs"""
        project, trees = complex_project
        
        # Create a large number of cross-tree dependencies
        dependency_count = 0
        
        # Create dependencies between all service pairs
        service_tasks = [
            ("20250625103", "20250625201"),  # Auth → User
            ("20250625201", "20250625301"),  # User → Product
            ("20250625301", "20250625401"),  # Product → Order
            ("20250625401", "20250625501"),  # Order → Payment
            ("20250625501", "20250625601"),  # Payment → Notification
            ("20250625102", "20250625202"),  # OAuth → User CRUD
            ("20250625302", "20250625402"),  # Product Search → Order State
            ("20250625403", "20250625502"),  # Order History → Transaction Security
            ("20250625503", "20250625602"),  # Payment Status → SMS Service
            ("20250625103", "20250625401"),  # Auth API → Order Processing (cross multiple layers)
        ]
        
        for dependent, prerequisite in service_tasks:
            project.add_cross_tree_dependency(dependent, prerequisite)
            dependency_count += 1
        
        # Measure coordination performance
        import time
        start_time = time.time()
        coordination_result = project.coordinate_cross_tree_dependencies()
        end_time = time.time()
        
        coordination_time = end_time - start_time
        
        # Verify the coordination completed successfully
        assert coordination_result["total_dependencies"] == dependency_count
        assert "validated_dependencies" in coordination_result
        
        # Performance should be reasonable (under 1 second for this scale)
        assert coordination_time < 1.0, f"Dependency coordination took {coordination_time:.3f}s, expected < 1.0s"
        
        # Verify dependencies are properly tracked (some may be invalid/missing)
        # The system may skip invalid dependencies, so validated count could be less
        assert coordination_result["validated_dependencies"] <= dependency_count
        assert coordination_result["validated_dependencies"] > 0
    
    @pytest.mark.integration
    def test_dynamic_dependency_updates(self, complex_project, dependency_tasks):
        """Test dynamic addition and removal of dependencies"""
        project, trees = complex_project
        
        # Start with simple dependency
        project.add_cross_tree_dependency("20250625401", "20250625301")  # Order → Product
        
        initial_result = project.coordinate_cross_tree_dependencies()
        assert initial_result["total_dependencies"] == 1
        assert "20250625401" in initial_result["blocked_tasks"]
        
        # Dynamically add more dependencies
        project.add_cross_tree_dependency("20250625401", "20250625202")  # Order → User
        project.add_cross_tree_dependency("20250625501", "20250625401")  # Payment → Order
        
        updated_result = project.coordinate_cross_tree_dependencies()
        assert updated_result["total_dependencies"] == 3
        
        # Complete prerequisite tasks to test dynamic resolution
        product_schema_task = None
        user_crud_task = None
        
        for task in dependency_tasks["product"]:
            if task.id.value == "20250625301":
                product_schema_task = task
                break
        
        for task in dependency_tasks["user"]:
            if task.id.value == "20250625202":
                user_crud_task = task
                break
        
        # Complete one prerequisite
        if product_schema_task:
            product_schema_task.status = TaskStatus("done")
            partial_result = project.coordinate_cross_tree_dependencies()
            # Order should still be blocked (needs User CRUD too)
            assert "20250625401" in partial_result["blocked_tasks"]
        
        # Complete second prerequisite
        if user_crud_task:
            user_crud_task.status = TaskStatus("done")
            final_result = project.coordinate_cross_tree_dependencies()
            # Now Order should be ready, and Payment should be blocked waiting for Order
            assert "20250625401" in final_result["ready_tasks"]
            assert "20250625501" in final_result["blocked_tasks"]
    
    @pytest.mark.integration
    def test_dependency_error_handling(self, complex_project, dependency_tasks):
        """Test error handling in dependency management"""
        project, trees = complex_project
        
        # Test adding dependency with non-existent task
        try:
            project.add_cross_tree_dependency("20250625999", "20250625301")  # Non-existent → Product
            coordination_result = project.coordinate_cross_tree_dependencies()
            
            # Should handle missing tasks gracefully
            missing_prereqs = coordination_result.get("missing_prerequisites", [])
            assert len(missing_prereqs) > 0
            
        except ValueError as e:
            # Alternatively, system might reject invalid dependencies upfront
            assert "not found" in str(e).lower()
        
        # Test dependency on task in same tree (should be rejected)
        with pytest.raises(ValueError, match="same tree"):
            project.add_cross_tree_dependency("20250625301", "20250625302")  # Product Schema → Product Search (same tree)
        
        # Test self-dependency (should be rejected)
        with pytest.raises(ValueError):
            project.add_cross_tree_dependency("20250625301", "20250625301")  # Self-dependency


if __name__ == "__main__":
    pytest.main([__file__, "-v"])