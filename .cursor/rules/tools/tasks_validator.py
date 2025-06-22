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

        if not isinstance(data, list):
            results["errors"].append(f"Root of {file_path} should be a list of tasks.")
            results["total_issues"] += 1
            results["summary"]["errors"] += 1
        
        # Basic check for task structure
        for i, task in enumerate(data):
            if not isinstance(task, dict):
                results["errors"].append(f"Task at index {i} is not a dictionary.")
                continue
            if 'id' not in task:
                results["warnings"].append(f"Task at index {i} is missing 'id' field.")
            if 'title' not in task:
                 results["warnings"].append(f"Task at index {i} is missing 'title' field.")


        if not results["errors"] and not results["warnings"]:
            results["validation_passed"] = True
        
        results["summary"]["errors"] = len(results["errors"])
        results["summary"]["warnings"] = len(results["warnings"])
        results["total_issues"] = results["summary"]["errors"] + results["summary"]["warnings"]
            
        return results

if __name__ == '__main__':
    # This allows running the script directly for testing
    validator = TasksValidator()
    result = validator.validate()
    print(json.dumps(result, indent=2))
