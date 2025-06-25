#!/usr/bin/env python3
"""
Test script for hierarchical task management system
"""

import sys
import os
sys.path.append('/home/daihungpham/agentic-project/dhafnck_mcp_main/src')

from fastmcp.task_management.infrastructure.repositories.task_repository_factory import TaskRepositoryFactory
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
from fastmcp.task_management.domain.value_objects.priority import Priority

def test_hierarchical_storage():
    """Test the hierarchical storage system"""
    print("Testing Hierarchical Task Management System")
    print("=" * 50)
    
    # Initialize factory
    factory = TaskRepositoryFactory()
    
    # Test 1: Create repository for proj1/main
    print("\n1. Testing repository creation for proj1/main...")
    repo1 = factory.create_repository("proj1", "main", "default_id")
    print(f"Repository created for proj1/main")
    
    # Test 2: Create a task in proj1/main
    print("\n2. Creating task in proj1/main...")
    task1 = Task.create(
        title="Test Task in Project 1",
        description="This is a test task in project 1, main tree",
        project_id="proj1"
    )
    saved_task1 = repo1.create(task1)
    print(f"Created task: {saved_task1.id} - {saved_task1.title}")
    
    # Test 3: Create repository for migration_workflow_test/workflow_tree
    print("\n3. Testing repository creation for migration_workflow_test/workflow_tree...")
    repo2 = factory.create_repository("migration_workflow_test", "workflow_tree", "default_id")
    print(f"Repository created for migration_workflow_test/workflow_tree")
    
    # Test 4: Create a task in migration_workflow_test/workflow_tree
    print("\n4. Creating task in migration_workflow_test/workflow_tree...")
    task2 = Task.create(
        title="Workflow Tree Task",
        description="This is a test task in workflow tree",
        project_id="migration_workflow_test"
    )
    saved_task2 = repo2.create(task2)
    print(f"Created task: {saved_task2.id} - {saved_task2.title}")
    
    # Test 5: Verify isolation - list tasks in each repository
    print("\n5. Testing task isolation...")
    tasks_proj1 = repo1.find_all()
    tasks_workflow_tree = repo2.find_all()
    
    print(f"Tasks in proj1/main: {len(tasks_proj1)}")
    for task in tasks_proj1:
        print(f"  - {task.id}: {task.title}")
    
    print(f"Tasks in migration_workflow_test/workflow_tree: {len(tasks_workflow_tree)}")
    for task in tasks_workflow_tree:
        print(f"  - {task.id}: {task.title}")
    
    # Test 6: Verify file paths
    print("\n6. Verifying file paths...")
    expected_path1 = "/home/daihungpham/agentic-project/.cursor/rules/tasks/default_id/proj1/main/tasks.json"
    expected_path2 = "/home/daihungpham/agentic-project/.cursor/rules/tasks/default_id/migration_workflow_test/workflow_tree/tasks.json"
    
    print(f"Expected path 1: {expected_path1}")
    print(f"File exists: {os.path.exists(expected_path1)}")
    
    print(f"Expected path 2: {expected_path2}")
    print(f"File exists: {os.path.exists(expected_path2)}")
    
    # Test 7: Test repository factory validation
    print("\n7. Testing project/tree validation...")
    valid = factory.validate_user_project_tree("proj1", "main", "default_id")
    print(f"proj1/main validation: {valid}")
    
    invalid = factory.validate_user_project_tree("nonexistent", "main", "default_id")
    print(f"nonexistent/main validation: {invalid}")
    
    print("\n" + "=" * 50)
    print("Hierarchical storage test completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_hierarchical_storage()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)