# 📚 Task Manager Agent Documentation

## Overview
The Task Manager Agent provides comprehensive task management capabilities through the dhafnck_mcp server. This documentation covers how agents can effectively use the task management system for project coordination and workflow orchestration.

## Core Components

### 1. Task Management System
- **Location**: `dhafnck_mcp_main/src/fastmcp/task_management/`
- **Architecture**: Clean Architecture with Domain-Driven Design
- **Test Coverage**: 55% (target: 80%)

### 2. MCP Tools Interface
The task management system exposes tools through the MCP (Model Context Protocol) interface:

#### Available Tools
- `manage_task` - Core task operations (create, update, list, complete, etc.)
- `manage_project` - Project lifecycle management 
- `manage_agent` - Multi-agent coordination
- `manage_subtask` - Subtask breakdown and tracking
- `call_agent` - Agent switching and configuration loading

## Usage Guide for Agents

### Basic Task Operations

#### Creating a Task
```python
# Through MCP tools
result = manage_task(
    action="create",
    title="Implement user authentication",
    description="Add JWT-based authentication system",
    priority="high",
    estimated_effort="medium",
    assignees=["@coding_agent"],
    labels=["feature", "security", "backend"]
)
```

#### Updating Task Status
```python
# Mark task as in progress
result = manage_task(
    action="update",
    task_id="task_123",
    status="in_progress"
)

# Complete a task
result = manage_task(
    action="complete",
    task_id="task_123"
)
```

#### Getting Next Task
```python
# Get the next recommended task
result = manage_task(action="next")
if result["success"] and result["next_item"]:
    next_task = result["next_item"]
    print(f"Next task: {next_task['title']}")
```

### Project Management

#### Creating a Project
```python
result = manage_project(
    action="create",
    project_id="web_app",
    name="E-commerce Website",
    description="Modern e-commerce platform with React and Node.js"
)
```

#### Agent Registration
```python
# Register an agent to a project
result = manage_agent(
    action="register",
    project_id="web_app",
    agent_id="frontend_dev",
    name="Frontend Developer",
    call_agent="@ui_designer_agent"
)
```

### Subtask Management

#### Breaking Down Tasks
```python
# Add subtasks to a main task
result = manage_subtask(
    action="add",
    task_id="task_123",
    subtask_data={
        "title": "Design login form",
        "description": "Create responsive login form component"
    }
)
```

### Agent Workflow Integration

#### Automatic Context Switching
When tasks are assigned to specific agents, the system automatically:
1. Loads agent-specific configuration from `yaml-lib/[agent_name]/`
2. Updates `.cursor/rules/auto_rule.mdc` with task context
3. Switches AI assistant behavior to match agent expertise

#### Agent Communication Pattern
```python
# 1. Get assigned task
task = manage_task(action="next")

# 2. Update status to in_progress
manage_task(action="update", task_id=task["id"], status="in_progress")

# 3. Work on the task...

# 4. Complete the task
manage_task(action="complete", task_id=task["id"])

# 5. Create follow-up tasks if needed
manage_task(
    action="create",
    title="Review implementation",
    assignees=["@code_reviewer_agent"]
)
```

## Advanced Features

### Dependency Management
```python
# Add task dependencies
result = manage_task(
    action="add_dependency",
    task_id="task_123",
    dependency_data={"dependency_id": "task_456"}
)
```

### Search and Filtering
```python
# Search tasks by content
result = manage_task(
    action="search",
    query="authentication",
    limit=10
)

# List tasks by status
result = manage_task(
    action="list",
    status="in_progress",
    assignees=["@coding_agent"]
)
```

## Best Practices

### 1. Task Granularity
- **Good**: "Implement JWT token validation"
- **Avoid**: "Build authentication system" (too broad)

### 2. Clear Assignees
- Always specify agent assignees using `@agent_name` format
- Primary assignee triggers automatic context switching

### 3. Meaningful Labels
- Use standard labels: `feature`, `bug`, `urgent`, `frontend`, `backend`
- Helps with filtering and prioritization

### 4. Estimated Effort
- Use standard efforts: `quick`, `short`, `small`, `medium`, `large`, `xlarge`
- Helps with sprint planning and resource allocation

## Error Handling

### Common Issues and Solutions

#### Task Not Found
```python
result = manage_task(action="get", task_id="invalid_id")
if not result["success"]:
    print(f"Error: {result['error']}")
    # Handle gracefully
```

#### Invalid Status Transition
```python
# Check current status before updating
task = manage_task(action="get", task_id="task_123")
if task["status"] != "done":
    # Safe to update
    manage_task(action="update", task_id="task_123", status="in_progress")
```

## Integration with CI/CD

### Automated Task Updates
```python
# In CI pipeline
def update_task_on_deployment(task_id: str, success: bool):
    if success:
        manage_task(action="complete", task_id=task_id)
    else:
        manage_task(
            action="update", 
            task_id=task_id, 
            status="blocked",
            details="Deployment failed - see CI logs"
        )
```

## Monitoring and Analytics

### Task Metrics
- Completion rates by agent
- Average task duration
- Blocked task analysis
- Sprint velocity tracking

### Available Dashboards
```python
# Get project dashboard
result = manage_project(action="dashboard", project_id="web_app")
```

## Testing Guidelines

### Unit Tests
- Test individual task operations
- Validate business rules
- Mock external dependencies

### Integration Tests
- Test MCP tool interactions
- Validate cross-agent workflows
- Test error scenarios

### Coverage Targets
- Domain layer: 80%+ (currently 70%)
- Application layer: 75%+ (currently 46%)
- Infrastructure layer: 70%+ (currently 54%)
- Interface layer: 60%+ (currently 31%)

## Troubleshooting

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger('fastmcp.task_management').setLevel(logging.DEBUG)
```

### Common Diagnostics
1. Check MCP server status
2. Validate task.json integrity
3. Verify agent configurations
4. Test database connections

## Future Enhancements

### Planned Features
- Real-time task updates via WebSocket
- Integration with external project management tools
- Advanced analytics and reporting
- Automated task estimation using ML

### Contributing
- Add tests for new features
- Follow clean architecture principles
- Update documentation
- Maintain backwards compatibility

---

*This documentation is generated for the dhafnck_mcp task management system.*
*Last updated: 2025-06-25*
*Coverage: 55% (target: 80%)*