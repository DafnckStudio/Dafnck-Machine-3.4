#!/usr/bin/env python3
"""
Test script to verify the context generation logic
"""

import sys
import os
# Add the src directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from fastmcp.task_management.application.use_cases.do_next import DoNextUseCase
from fastmcp.task_management.infrastructure.services.context_generate import generate_context_content_for_mcp
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
from fastmcp.task_management.domain.value_objects.priority import Priority

def test_should_generate_context_info():
    """Test the _should_generate_context_info logic"""
    
    # Mock DoNextUseCase to test the logic
    use_case = DoNextUseCase(None, None)
    
    print("🧪 Testing _should_generate_context_info logic...")
    
    # Test case 1: todo task with no subtasks - should generate
    task1 = Task(
        id=TaskId("20250127001"),
        title="Test Task 1",
        description="Test",
        status=TaskStatus.TODO,
        priority=Priority.MEDIUM,
        subtasks=[]
    )
    result1 = use_case._should_generate_context_info(task1)
    print(f"✅ Task 1 (todo, no subtasks): {result1} (expected: True)")
    
    # Test case 2: todo task with incomplete subtasks - should generate
    task2 = Task(
        id=TaskId("20250127002"),
        title="Test Task 2", 
        description="Test",
        status=TaskStatus.TODO,
        priority=Priority.MEDIUM,
        subtasks=[
            {"id": "20250127002.1", "title": "Subtask 1", "completed": False},
            {"id": "20250127002.2", "title": "Subtask 2", "completed": False}
        ]
    )
    result2 = use_case._should_generate_context_info(task2)
    print(f"✅ Task 2 (todo, incomplete subtasks): {result2} (expected: True)")
    
    # Test case 3: todo task with some completed subtasks - should NOT generate
    task3 = Task(
        id=TaskId("20250127003"),
        title="Test Task 3",
        description="Test", 
        status=TaskStatus.TODO,
        priority=Priority.MEDIUM,
        subtasks=[
            {"id": "20250127003.1", "title": "Subtask 1", "completed": True},
            {"id": "20250127003.2", "title": "Subtask 2", "completed": False}
        ]
    )
    result3 = use_case._should_generate_context_info(task3)
    print(f"✅ Task 3 (todo, some completed subtasks): {result3} (expected: False)")
    
    # Test case 4: in_progress task - should NOT generate  
    task4 = Task(
        id=TaskId("20250127004"),
        title="Test Task 4",
        description="Test",
        status=TaskStatus.IN_PROGRESS,
        priority=Priority.MEDIUM,
        subtasks=[]
    )
    result4 = use_case._should_generate_context_info(task4)
    print(f"✅ Task 4 (in_progress, no subtasks): {result4} (expected: False)")
    
    # Test case 5: done task - should NOT generate
    task5 = Task(
        id=TaskId("20250127005"),
        title="Test Task 5",
        description="Test",
        status=TaskStatus.DONE,
        priority=Priority.MEDIUM,
        subtasks=[]
    )
    result5 = use_case._should_generate_context_info(task5)
    print(f"✅ Task 5 (done, no subtasks): {result5} (expected: False)")
    
    print("\n🎯 Summary:")
    print(f"- Context generation should be enabled for todo tasks with no completed subtasks")
    print(f"- Context generation should be disabled for non-todo tasks or tasks with completed subtasks")
    
    return all([result1, result2, not result3, not result4, not result5])

def test_generate_context_content():
    """Test the context content generation function"""
    
    print("\n🧪 Testing generate_context_content_for_mcp...")
    
    # Create a test task
    task = Task(
        id=TaskId("20250127100"),
        title="Test Context Generation",
        description="Testing context file generation",
        status=TaskStatus.TODO,
        priority=Priority.HIGH,
        details="This is a test task for context generation",
        assignees=["@coding_agent", "@test_agent"],
        labels=["test", "context"]
    )
    
    try:
        content, file_path = generate_context_content_for_mcp(task, user_id="test_user")
        
        print(f"✅ Content generated successfully")
        print(f"✅ File path: {file_path}")
        print(f"✅ Content length: {len(content)} characters")
        print(f"✅ Content preview: {content[:200]}...")
        
        # Check if content contains expected elements
        expected_elements = [
            "20250127100",
            "Test Context Generation", 
            "coding_agent",
            "test_agent",
            "test",
            "context"
        ]
        
        missing_elements = []
        for element in expected_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing elements in content: {missing_elements}")
            return False
        else:
            print(f"✅ All expected elements found in content")
            return True
            
    except Exception as e:
        print(f"❌ Error generating context content: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Context Generation Logic\n")
    
    test1_passed = test_should_generate_context_info()
    test2_passed = test_generate_context_content()
    
    print(f"\n📊 Test Results:")
    print(f"- Context logic test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"- Content generation test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All tests passed! Context generation logic is working correctly.")
        sys.exit(0)
    else:
        print(f"\n💥 Some tests failed. Please check the implementation.")
        sys.exit(1) 