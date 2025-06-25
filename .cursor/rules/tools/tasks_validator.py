import json
import os

class TasksValidator:
    def __init__(self, file_path=None):
        if file_path:
            self.file_path = file_path
        else:
            # This is a default, but the tool should provide the correct path.
            # This logic assumes the script is run from the project root.
            self.file_path = os.path.join(os.getcwd(), '.cursor', 'rules', 'tasks', 'tasks.json')

    def validate(self):
        results = {
            "file_path": str(self.file_path),
            "file_exists": False,
            "validation_passed": False,
            "total_issues": 0,
            "summary": {"errors": 0, "warnings": 0, "missing_properties": 0},
            "errors": [],
            "warnings": [],
            "missing_properties": [],
            "recommendations": []
        }

        # The path from the tool can be a Path object
        file_path = str(self.file_path)

        if not os.path.exists(file_path):
            results["errors"].append(f"tasks.json file not found at {file_path}")
            results["total_issues"] += 1
            results["summary"]["errors"] += 1
            return results

        results["file_exists"] = True

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            results["errors"].append(f"Invalid JSON in {file_path}: {e}")
            results["total_issues"] += 1
            results["summary"]["errors"] += 1
            return results

        # Handle both hierarchical structure (with metadata) and legacy list structure
        if isinstance(data, dict):
            # New hierarchical structure with metadata
            if 'tasks' not in data:
                results["errors"].append(f"Hierarchical tasks.json missing 'tasks' field in {file_path}")
                results["total_issues"] += 1
                results["summary"]["errors"] += 1
                return results
            
            # Validate metadata if present
            if 'metadata' in data:
                metadata = data['metadata']
                required_metadata = ['version', 'project_id', 'task_tree_id', 'user_id']
                for field in required_metadata:
                    if field not in metadata:
                        results["missing_properties"].append(f"Missing metadata field: {field}")
                        results["summary"]["missing_properties"] += 1
            else:
                results["warnings"].append("Missing metadata section in hierarchical structure")
                results["summary"]["warnings"] += 1
            
            tasks = data['tasks']
        elif isinstance(data, list):
            # Legacy list structure
            tasks = data
            results["warnings"].append("Using legacy list structure; consider upgrading to hierarchical format")
            results["summary"]["warnings"] += 1
        else:
            results["errors"].append(f"Root of {file_path} should be a dictionary (hierarchical) or list (legacy).")
            results["total_issues"] += 1
            results["summary"]["errors"] += 1
            return results
        
        # Validate task structure
        task_ids = set()
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                results["errors"].append(f"Task at index {i} is not a dictionary.")
                results["summary"]["errors"] += 1
                continue
                
            # Check required fields
            required_fields = ['id', 'title', 'status', 'priority']
            for field in required_fields:
                if field not in task:
                    results["missing_properties"].append(f"Task at index {i} missing required field: {field}")
                    results["summary"]["missing_properties"] += 1
            
            # Check for duplicate IDs
            if 'id' in task:
                task_id = task['id']
                if task_id in task_ids:
                    results["errors"].append(f"Duplicate task ID found: {task_id}")
                    results["summary"]["errors"] += 1
                else:
                    task_ids.add(task_id)
            
            # Validate status values
            if 'status' in task:
                valid_statuses = ['todo', 'in_progress', 'blocked', 'review', 'testing', 'done', 'cancelled']
                if task['status'] not in valid_statuses:
                    results["warnings"].append(f"Task {task.get('id', f'at index {i}')} has invalid status: {task['status']}")
                    results["summary"]["warnings"] += 1
            
            # Validate priority values
            if 'priority' in task:
                valid_priorities = ['low', 'medium', 'high', 'urgent', 'critical']
                if task['priority'] not in valid_priorities:
                    results["warnings"].append(f"Task {task.get('id', f'at index {i}')} has invalid priority: {task['priority']}")
                    results["summary"]["warnings"] += 1
            
            # Validate dependencies if present
            if 'dependencies' in task and task['dependencies']:
                for dep_id in task['dependencies']:
                    if dep_id not in task_ids and dep_id not in [t.get('id') for t in tasks[i+1:]]:
                        results["warnings"].append(f"Task {task.get('id', f'at index {i}')} references unknown dependency: {dep_id}")
                        results["summary"]["warnings"] += 1


        # Add recommendations based on findings
        if results["summary"]["missing_properties"] > 0:
            results["recommendations"].append("Consider adding missing required fields to improve task management")
        
        if results["summary"]["warnings"] > 0 and any("legacy list structure" in w for w in results["warnings"]):
            results["recommendations"].append("Upgrade to hierarchical task structure for better organization")
        
        if results["summary"]["errors"] == 0 and results["summary"]["warnings"] == 0 and results["summary"]["missing_properties"] == 0:
            results["validation_passed"] = True
            results["recommendations"].append("Task structure is well-formed and compliant")
        
        # Calculate totals
        results["summary"]["errors"] = len(results["errors"])
        results["summary"]["warnings"] = len(results["warnings"])
        results["summary"]["missing_properties"] = len(results["missing_properties"])
        results["total_issues"] = results["summary"]["errors"] + results["summary"]["warnings"] + results["summary"]["missing_properties"]
            
        return results

if __name__ == '__main__':
    # This allows running the script directly for testing
    validator = TasksValidator()
    result = validator.validate()
    print(json.dumps(result, indent=2))
