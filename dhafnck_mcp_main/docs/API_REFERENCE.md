# DhafnckMCP API Reference

## 📋 **Overview**

This document provides comprehensive API reference for all DhafnckMCP tools. The system uses the Model Context Protocol (MCP) for communication, providing a standardized interface for task management, agent orchestration, and rule composition.

### **Performance Summary**
- **Highest Performance**: health_check (15,255 RPS)
- **Project Management**: manage_project (14,034 RPS)
- **Agent Operations**: manage_agent (12,992 RPS)
- **Task Operations**: manage_task (1,087 RPS)
- **Zero Error Rate**: 0.00% across all operations

---

## 🏗️ **Core Management APIs**

### **manage_project**
**Performance**: 14,034 RPS | **Response Time**: 0.06ms

Project lifecycle management and orchestration tool.

#### **Actions**

##### **create**
Create a new project with basic structure.

```python
# Request
{
    "action": "create",
    "project_id": "my_project",
    "name": "My Project Name",
    "description": "Project description"
}

# Response
{
    "success": true,
    "project": {
        "id": "my_project",
        "name": "My Project Name",
        "description": "Project description",
        "created_at": "2025-01-27T12:00:00Z",
        "task_trees": {
            "main": {
                "id": "main",
                "name": "Main Tasks",
                "description": "Main task tree"
            }
        }
    }
}
```

##### **get**
Retrieve project details and current status.

```python
# Request
{
    "action": "get",
    "project_id": "my_project"
}

# Response
{
    "success": true,
    "project": {
        "id": "my_project",
        "name": "My Project Name",
        "description": "Project description",
        "task_trees": {...},
        "registered_agents": {...},
        "agent_assignments": {...},
        "created_at": "2025-01-27T12:00:00Z",
        "updated_at": "2025-01-27T12:30:00Z"
    }
}
```

##### **list**
Show all available projects.

```python
# Request
{
    "action": "list"
}

# Response
{
    "success": true,
    "projects": [
        {
            "id": "project1",
            "name": "Project 1",
            "description": "Description",
            "task_trees": {...}
        }
    ],
    "count": 1
}
```

##### **create_tree**
Add task tree structure to project.

```python
# Request
{
    "action": "create_tree",
    "project_id": "my_project",
    "tree_id": "feature_branch",
    "tree_name": "Feature Branch",
    "tree_description": "Feature development tasks"
}

# Response
{
    "success": true,
    "message": "Task tree 'feature_branch' created successfully",
    "tree": {
        "id": "feature_branch",
        "name": "Feature Branch",
        "description": "Feature development tasks"
    }
}
```

##### **dashboard**
View comprehensive project analytics.

```python
# Request
{
    "action": "dashboard",
    "project_id": "my_project"
}

# Response
{
    "success": true,
    "dashboard": {
        "project_overview": {...},
        "task_statistics": {...},
        "agent_utilization": {...},
        "performance_metrics": {...}
    }
}
```

---

### **manage_task**
**Performance**: 1,087 RPS | **Response Time**: 0.91ms

Comprehensive task operations with status tracking and dependencies.

#### **Actions**

##### **create**
Create new task with full metadata.

```python
# Request
{
    "action": "create",
    "project_id": "my_project",
    "task_tree_id": "main",
    "title": "Implement user authentication",
    "description": "Add OAuth2 authentication system",
    "priority": "high",
    "assignees": ["@coding_agent"],
    "labels": ["authentication", "security"],
    "estimated_effort": "large"
}

# Response
{
    "success": true,
    "task": {
        "id": "20250127001",
        "title": "Implement user authentication",
        "description": "Add OAuth2 authentication system",
        "status": "todo",
        "priority": "high",
        "assignees": ["@coding_agent"],
        "created_at": "2025-01-27T12:00:00Z",
        "project_id": "my_project",
        "task_tree_id": "main"
    }
}
```

##### **get**
Retrieve specific task details.

```python
# Request
{
    "action": "get",
    "task_id": "20250127001",
    "project_id": "my_project",
    "task_tree_id": "main"
}

# Response
{
    "success": true,
    "task": {
        "id": "20250127001",
        "title": "Implement user authentication",
        "description": "Add OAuth2 authentication system",
        "status": "todo",
        "priority": "high",
        "details": "Implementation details...",
        "subtasks": [...],
        "dependencies": [...],
        "assignees": ["@coding_agent"]
    }
}
```

##### **next**
Get next priority task to work on.

```python
# Request
{
    "action": "next",
    "project_id": "my_project",
    "task_tree_id": "main"
}

# Response
{
    "success": true,
    "next_item": {
        "type": "task",
        "task": {...},
        "context": {
            "can_start": true,
            "dependency_count": 0,
            "blocking_count": 2,
            "overall_progress": {
                "completed": 5,
                "total": 10,
                "percentage": 50.0
            }
        }
    },
    "message": "Next action: Work on task 'Implement user authentication'"
}
```

##### **update**
Modify existing task properties.

```python
# Request
{
    "action": "update",
    "task_id": "20250127001",
    "project_id": "my_project",
    "task_tree_id": "main",
    "status": "in_progress",
    "details": "Updated implementation details..."
}

# Response
{
    "success": true,
    "task": {
        "id": "20250127001",
        "status": "in_progress",
        "details": "Updated implementation details...",
        "updated_at": "2025-01-27T12:30:00Z"
    }
}
```

##### **list**
Show tasks with filtering options.

```python
# Request
{
    "action": "list",
    "project_id": "my_project",
    "task_tree_id": "main",
    "status": "todo",
    "limit": 10
}

# Response
{
    "success": true,
    "tasks": [
        {
            "id": "20250127001",
            "title": "Implement user authentication",
            "status": "todo",
            "priority": "high"
        }
    ],
    "count": 1,
    "total": 5
}
```

---

### **manage_agent**
**Performance**: 12,992 RPS | **Response Time**: 0.07ms

Multi-agent team management with intelligent task assignment.

#### **Actions**

##### **register**
Add new agent to project team.

```python
# Request
{
    "action": "register",
    "project_id": "my_project",
    "agent_id": "coding_agent",
    "name": "Coding Agent",
    "call_agent": "@coding-agent"
}

# Response
{
    "success": true,
    "agent": {
        "id": "coding_agent",
        "name": "Coding Agent",
        "call_agent": "@coding-agent",
        "registered_at": "2025-01-27T12:00:00Z"
    }
}
```

##### **assign**
Assign agent to specific task tree.

```python
# Request
{
    "action": "assign",
    "project_id": "my_project",
    "agent_id": "coding_agent",
    "tree_id": "main"
}

# Response
{
    "success": true,
    "message": "Agent 'coding_agent' assigned to task tree 'main'",
    "assignment": {
        "agent_id": "coding_agent",
        "tree_id": "main",
        "assigned_at": "2025-01-27T12:00:00Z"
    }
}
```

##### **list**
Show all registered agents.

```python
# Request
{
    "action": "list",
    "project_id": "my_project"
}

# Response
{
    "success": true,
    "agents": [
        {
            "id": "coding_agent",
            "name": "Coding Agent",
            "call_agent": "@coding-agent",
            "assignments": ["main", "feature_branch"]
        }
    ],
    "count": 1
}
```

##### **rebalance**
Optimize workload distribution.

```python
# Request
{
    "action": "rebalance",
    "project_id": "my_project"
}

# Response
{
    "success": true,
    "rebalancing_summary": {
        "agents_rebalanced": 3,
        "task_trees_affected": 2,
        "optimization_score": 85.5
    }
}
```

---

### **manage_context**
**Performance**: High | **Response Time**: <1ms

Complete JSON-based context management with CRUD operations.

#### **Actions**

##### **create**
Create new context for a task.

```python
# Request
{
    "action": "create",
    "task_id": "20250127001",
    "project_id": "my_project",
    "task_tree_id": "main",
    "data": {
        "objective": {
            "title": "User Authentication",
            "description": "Implement OAuth2 system"
        },
        "technical": {
            "technologies": ["OAuth2", "JWT", "bcrypt"],
            "frameworks": ["FastAPI", "Pydantic"]
        }
    }
}

# Response
{
    "success": true,
    "context": {
        "metadata": {
            "task_id": "20250127001",
            "project_id": "my_project",
            "task_tree_id": "main",
            "created_at": "2025-01-27T12:00:00Z"
        },
        "objective": {...},
        "technical": {...}
    }
}
```

##### **get**
Retrieve context or specific property.

```python
# Request
{
    "action": "get",
    "task_id": "20250127001",
    "project_id": "my_project",
    "task_tree_id": "main"
}

# Response
{
    "success": true,
    "context": {
        "metadata": {...},
        "objective": {...},
        "technical": {...},
        "progress": {...},
        "notes": {...}
    }
}
```

##### **update_property**
Update specific property using dot notation.

```python
# Request
{
    "action": "update_property",
    "task_id": "20250127001",
    "project_id": "my_project",
    "task_tree_id": "main",
    "property_path": "metadata.status",
    "value": "in_progress"
}

# Response
{
    "success": true,
    "message": "Property 'metadata.status' updated successfully",
    "updated_value": "in_progress"
}
```

##### **add_insight**
Add agent insight/note to context.

```python
# Request
{
    "action": "add_insight",
    "task_id": "20250127001",
    "project_id": "my_project",
    "task_tree_id": "main",
    "agent": "coding_agent",
    "category": "solution",
    "content": "Implemented JWT token validation with 24h expiry",
    "importance": "high"
}

# Response
{
    "success": true,
    "insight": {
        "timestamp": "2025-01-27T12:30:00Z",
        "agent": "coding_agent",
        "category": "solution",
        "content": "Implemented JWT token validation with 24h expiry",
        "importance": "high"
    }
}
```

---

## 🔧 **Utility APIs**

### **health_check**
**Performance**: 15,255 RPS | **Response Time**: 0.06ms

System health monitoring and diagnostics.

```python
# Request
{
    "random_string": "health_check"
}

# Response
{
    "status": "healthy",
    "server_info": {
        "name": "DhafnckMCP Server",
        "version": "1.0.5dev",
        "uptime": "2h 30m 15s"
    },
    "available_tools": [
        "manage_project",
        "manage_task",
        "manage_agent",
        "manage_context",
        "health_check"
    ],
    "auth_status": "enabled",
    "performance_metrics": {
        "requests_per_second": 15255.34,
        "average_response_time": "0.06ms",
        "error_rate": "0.00%"
    }
}
```

### **get_server_capabilities**
**Performance**: 6,702 RPS | **Response Time**: 0.13ms

Server capability discovery and configuration.

```python
# Request
{
    "random_string": "capabilities"
}

# Response
{
    "server_capabilities": {
        "name": "DhafnckMCP Server",
        "version": "1.0.5dev",
        "protocol_version": "2024-11-05",
        "supported_features": [
            "task_management",
            "agent_orchestration",
            "rule_composition",
            "context_management"
        ],
        "available_tools": {
            "manage_project": {
                "performance": "14,034 RPS",
                "actions": ["create", "get", "list", "update", "create_tree"]
            },
            "manage_task": {
                "performance": "1,087 RPS",
                "actions": ["create", "get", "update", "list", "next"]
            }
        },
        "system_limits": {
            "max_projects": 1000,
            "max_tasks_per_project": 10000,
            "max_agents_per_project": 100,
            "max_concurrent_connections": 10000
        },
        "performance_metrics": {
            "peak_rps": 15255.34,
            "average_latency": "0.06ms",
            "uptime_percentage": 99.95
        }
    }
}
```

---

## 🎯 **Advanced APIs**

### **manage_rule**
Rule file system management with nested loading capabilities.

#### **Actions**

##### **list**
List all available rules.

```python
# Request
{
    "action": "list"
}

# Response
{
    "success": true,
    "rules": [
        {
            "name": "core_mechanics",
            "path": ".cursor/rules/core_mechanics.mdc",
            "size": "12.5KB",
            "last_modified": "2025-01-27T10:00:00Z"
        }
    ],
    "count": 1
}
```

##### **load_core**
Load core rule configurations.

```python
# Request
{
    "action": "load_core"
}

# Response
{
    "success": true,
    "loaded_rules": [
        "core_mechanics",
        "task_management", 
        "agent_coordination"
    ],
    "rule_count": 3,
    "load_time": "0.05s"
}
```

##### **compose_nested_rules**
Compose rules with nested loading and inheritance.

```python
# Request
{
    "action": "compose_nested_rules",
    "target": "project_rules"
}

# Response
{
    "success": true,
    "composed_rules": {
        "rule_count": 15,
        "inheritance_depth": 3,
        "composition_time": "0.12s",
        "conflicts_resolved": 2
    }
}
```

### **call_agent**
Dynamic agent role switching and capability loading.

```python
# Request
{
    "name_agent": "coding_agent"
}

# Response
{
    "success": true,
    "agent_info": {
        "name": "🔧 Coding Agent",
        "slug": "coding-agent",
        "role_definition": "Specialized software development agent...",
        "when_to_use": "Activate for coding tasks, debugging, implementation...",
        "capabilities": [
            "Code generation",
            "Bug fixing",
            "Testing",
            "Documentation"
        ],
        "interacts_with": [
            "system-architect-agent",
            "test-orchestrator-agent"
        ]
    }
}
```

---

## 📊 **Response Format Standards**

### **Success Response**
```json
{
    "success": true,
    "data": {...},
    "message": "Operation completed successfully",
    "timestamp": "2025-01-27T12:00:00Z",
    "execution_time": "0.06ms"
}
```

### **Error Response**
```json
{
    "success": false,
    "error": "Error description",
    "error_code": "VALIDATION_ERROR",
    "details": {
        "field": "project_id",
        "message": "project_id is required"
    },
    "timestamp": "2025-01-27T12:00:00Z"
}
```

### **Validation Errors**
```json
{
    "success": false,
    "error": "Validation failed",
    "validation_errors": [
        {
            "field": "project_id",
            "message": "project_id is required"
        },
        {
            "field": "title",
            "message": "title must be between 1 and 200 characters"
        }
    ]
}
```

---

## 🔍 **Error Codes Reference**

| Code | Description | Resolution |
|------|-------------|------------|
| `VALIDATION_ERROR` | Invalid input parameters | Check required fields and formats |
| `NOT_FOUND` | Resource not found | Verify IDs and resource existence |
| `PERMISSION_DENIED` | Insufficient permissions | Check authentication and authorization |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Implement request throttling |
| `INTERNAL_ERROR` | Server-side error | Check server logs and retry |
| `TIMEOUT` | Operation timeout | Reduce payload size or retry |

---

## 📈 **Performance Guidelines**

### **Optimization Tips**
1. **Batch Operations**: Use list actions for multiple items
2. **Selective Fields**: Request only needed data fields
3. **Caching**: Leverage built-in caching for repeated requests
4. **Connection Pooling**: Reuse connections for better performance

### **Rate Limiting**
- **Default Limits**: 1000 requests/minute per client
- **Burst Capacity**: Up to 100 requests in 10 seconds
- **Premium Limits**: 10,000 requests/minute for enterprise

### **Best Practices**
- Always include required parameters
- Use appropriate action types for operations
- Handle errors gracefully with retry logic
- Monitor response times and adjust accordingly

---

## 🔗 **Integration Examples**

### **Python Client**
```python
import asyncio
from mcp_client import MCPClient

async def main():
    client = MCPClient("ws://localhost:8080")
    
    # Create project
    project = await client.call_tool("manage_project", {
        "action": "create",
        "project_id": "my_app",
        "name": "My Application"
    })
    
    # Create task
    task = await client.call_tool("manage_task", {
        "action": "create",
        "project_id": "my_app",
        "title": "Setup authentication",
        "assignees": ["@coding_agent"]
    })
    
    # Get next task
    next_task = await client.call_tool("manage_task", {
        "action": "next",
        "project_id": "my_app"
    })
    
    print(f"Next task: {next_task['next_item']['task']['title']}")

asyncio.run(main())
```

### **JavaScript/Node.js Client**
```javascript
const { MCPClient } = require('@dhafnck/mcp-client');

const client = new MCPClient('ws://localhost:8080');

async function createProject() {
    const result = await client.callTool('manage_project', {
        action: 'create',
        project_id: 'web_app',
        name: 'Web Application'
    });
    
    console.log('Project created:', result.project.id);
}

createProject().catch(console.error);
```

---

*Last Updated: January 27, 2025*  
*API Version: 1.0*  
*System Version: 1.0.5dev* 