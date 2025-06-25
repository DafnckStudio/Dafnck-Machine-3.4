"""Cursor Rules Management Tools for MCP Server"""

from typing import Dict, Any, Optional, Annotated
from pathlib import Path
import json
import os
import re
from pydantic import Field

from ..domain.services import AutoRuleGenerator

from fastmcp.tools.tool_path import find_project_root


def resolve_path(path, base=None):
    p = Path(path)
    if p.is_absolute():
        return p
    base = base or Path(__file__).parent
    return (base / p).resolve()


class CursorRulesTools:
    """Tools for managing Cursor rules and auto_rule.mdc file"""
    
    def __init__(self):
        from ..infrastructure.services import FileAutoRuleGenerator
        self._auto_rule_generator = FileAutoRuleGenerator()
    
    @property
    def project_root(self):
        # Allow override via environment variable, else use canonical function
        if "PROJECT_ROOT_PATH" in os.environ:
            return resolve_path(os.environ["PROJECT_ROOT_PATH"])
        return find_project_root()
    
    def register_tools(self, mcp):
        """Register all cursor rules tools with the MCP server"""
        
        @mcp.tool()
        def update_auto_rule(
            content: Annotated[str, Field(description="Complete markdown content for auto_rule.mdc file")],
            backup: Annotated[bool, Field(description="Create backup before update (default: true, recommended)")] = True
        ) -> Dict[str, Any]:
            """📝 AUTO-RULE CONTENT MANAGER - Direct update of AI assistant context rules

⭐ WHAT IT DOES: Updates .cursor/rules/auto_rule.mdc with custom AI context and rules
📋 WHEN TO USE: Manual context customization, special project rules, AI behavior tuning
🎯 CRITICAL FOR: Advanced users who need precise AI assistant configuration

🔧 FUNCTIONALITY:
• Direct Content Update: Replaces entire auto_rule.mdc with provided content
• Automatic Backup: Creates .mdc.backup before changes (unless disabled)
• Directory Creation: Ensures .cursor/rules/ directory structure exists
• Encoding Safety: Handles UTF-8 content with proper error handling

📋 PARAMETERS:
• content (required): Complete markdown content for auto_rule.mdc file
• backup (optional): Create backup before update (default: true, recommended)

⚠️ ADVANCED USAGE WARNING:
• Direct Editing: Bypasses task-based auto-generation
• Manual Responsibility: You must ensure proper markdown formatting
• Context Integrity: Content should follow established rule patterns
• Backup Recommended: Always use backup=true for safety

💡 CONTENT GUIDELINES:
• Use markdown headers for structure (# ## ###)
• Include task context if applicable
• Define clear role and persona information
• Specify operating rules and constraints
• Add tool usage guidance as needed

🎯 USE CASES:
• Custom Workflows: Project-specific AI behavior requirements
• Template Testing: Experimenting with rule formats
• Emergency Override: Quick context fixes when auto-generation fails
• Integration Setup: Preparing context for external integrations
            """
            try:
                auto_rule_path = self.project_root / ".cursor" / "rules" / "auto_rule.mdc"
                
                # Create backup if requested
                if backup and auto_rule_path.exists():
                    backup_path = auto_rule_path.with_suffix('.mdc.backup')
                    with open(auto_rule_path, 'r', encoding='utf-8') as src:
                        backup_content = src.read()
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(backup_content)
                
                # Ensure directory exists
                auto_rule_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write new content
                with open(auto_rule_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "message": "Auto rule file updated successfully",
                    "file_path": str(auto_rule_path),
                    "backup_created": backup and auto_rule_path.exists()
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to update auto rule: {str(e)}"
                }
        
        @mcp.tool()
        def validate_rules(
            file_path: Annotated[Optional[str], Field(description="Specific rule file to validate (default: auto_rule.mdc). Supports relative and absolute paths")] = None
        ) -> Dict[str, Any]:
            """🔍 RULES VALIDATION ENGINE - Comprehensive rule file quality and structure analysis

⭐ WHAT IT DOES: Analyzes rule files for proper structure, content quality, and potential issues
📋 WHEN TO USE: After rule modifications, troubleshooting AI behavior, quality assurance
🎯 ESSENTIAL FOR: Ensuring reliable AI assistant performance and context integrity

🔬 VALIDATION ANALYSIS:

📁 FILE INTEGRITY:
• Existence Check: Confirms file exists and is accessible
• Encoding Validation: Ensures UTF-8 compatibility and readability
• Size Analysis: Detects too-small files that lack sufficient context
• Line Count: Provides content volume metrics

📋 CONTENT STRUCTURE:
• Markdown Format: Validates proper markdown header structure
• Task Context: Checks for essential task information sections
• Role Definition: Ensures AI persona and role clarity
• Operating Rules: Validates presence of behavioral guidelines

🚨 ISSUE DETECTION:
• Content Deficiencies: Identifies missing critical sections
• Format Problems: Detects structural inconsistencies
• Size Warnings: Flags potentially insufficient context
• Encoding Errors: Catches character encoding issues

📋 PARAMETERS:
• file_path (optional): Specific rule file to validate (default: auto_rule.mdc)
• Path Handling: Supports both relative and absolute paths

💡 QUALITY METRICS:
• Completeness Score: How well the file covers required sections
• Structure Health: Markdown formatting quality assessment
• Content Density: Adequate information for AI context
• Integration Readiness: Suitability for AI assistant usage

🎯 USE CASES:
• Rule Development: Validate changes before deployment
• Troubleshooting: Diagnose AI behavior inconsistencies
• Quality Assurance: Ensure rule files meet standards
• Integration Testing: Verify rule compatibility
• Maintenance: Regular health checks of rule system
            """
            try:
                if file_path is None:
                    target_path = self.project_root / ".cursor" / "rules" / "auto_rule.mdc"
                else:
                    # If relative path provided, make it relative to project root
                    if not os.path.isabs(file_path):
                        target_path = self.project_root / file_path
                    else:
                        target_path = Path(file_path)
                
                if not target_path.exists():
                    return {
                        "success": False,
                        "error": f"File not found: {target_path}"
                    }
                
                # Read and validate content
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic validation checks
                validation_results = {
                    "file_exists": True,
                    "file_size": len(content),
                    "line_count": len(content.splitlines()),
                    "has_task_context": "Task Context" in content,
                    "has_role_info": "Role" in content or "Persona" in content,
                    "has_rules": "Rules" in content or "Operating" in content,
                    "markdown_structure": content.strip().startswith('#'),
                    "encoding_valid": True  # If we got here, encoding is valid
                }
                
                # Check for common issues
                issues = []
                if validation_results["file_size"] < 100:
                    issues.append("File seems too small (< 100 characters)")
                if not validation_results["has_task_context"]:
                    issues.append("Missing task context section")
                if not validation_results["markdown_structure"]:
                    issues.append("File doesn't start with markdown header")
                
                return {
                    "success": True,
                    "validation_results": validation_results,
                    "issues": issues,
                    "file_path": str(target_path)
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Validation failed: {str(e)}"
                }
        
        @mcp.tool()
        def manage_cursor_rules(
            action: Annotated[str, Field(description="Rule management action to perform. Available: list, backup, restore, clean, info")],
            target: Annotated[Optional[str], Field(description="Target file or directory (optional, context-dependent)")] = None,
            content: Annotated[Optional[str], Field(description="Content for write operations (optional, context-dependent)")] = None
        ) -> Dict[str, Any]:
            """🗂️ CURSOR RULES ADMINISTRATION - Complete rule file system management

⭐ WHAT IT DOES: Comprehensive management of .cursor/rules/ directory and rule files
📋 WHEN TO USE: Rule system maintenance, backup management, directory administration
🎯 ESSENTIAL FOR: System administrators, rule system maintenance, disaster recovery

📋 SUPPORTED ACTIONS & PARAMETERS:

📂 LIST: Discover all rule files in system
• Required: action="list"
• Returns: Complete inventory of .mdc files with metadata
• Metadata: File paths, sizes, modification timestamps
• Use Case: Rule system audit, finding configuration files

💾 BACKUP: Create safety copy of auto_rule.mdc
• Required: action="backup"
• Creates: auto_rule.mdc.backup in same directory
• Safety: Preserves current state before modifications
• Use Case: Pre-change safety, disaster recovery preparation

🔄 RESTORE: Recover from backup file
• Required: action="restore"
• Restores: auto_rule.mdc from .backup file
• Recovery: Reverses changes to last backup point
• Use Case: Rollback after problematic changes

🧹 CLEAN: Remove backup files
• Required: action="clean"
• Removes: All .backup files to free space
• Maintenance: Cleanup old backup files
• Use Case: Disk space management, system cleanup

📊 INFO: Get rules directory statistics
• Required: action="info"
• Returns: Directory structure, file counts, total sizes
• Overview: Complete rule system health summary
• Use Case: System monitoring, capacity planning

💡 ADMINISTRATIVE FEATURES:
• Path Safety: All operations contained within .cursor/rules/
• Error Handling: Graceful failure with descriptive messages
• Metadata Rich: Detailed information about all operations
• Cross-Platform: Works on Windows, macOS, and Linux

🎯 OPERATIONAL BENEFITS:
• System Maintenance: Keep rule system healthy and organized
• Disaster Recovery: Backup and restore capabilities
• Audit Trail: Track rule file changes and modifications
• Space Management: Clean up unnecessary backup files
            """
            try:
                rules_dir = self.project_root / ".cursor" / "rules"
                
                if action == "list":
                    if not rules_dir.exists():
                        return {
                            "success": True,
                            "files": [],
                            "message": "Rules directory does not exist"
                        }
                    
                    rule_files = []
                    for file_path in rules_dir.rglob("*.mdc"):
                        rule_files.append({
                            "path": str(file_path.relative_to(self.project_root)),
                            "size": file_path.stat().st_size,
                            "modified": file_path.stat().st_mtime
                        })
                    
                    return {
                        "success": True,
                        "files": rule_files,
                        "count": len(rule_files)
                    }
                
                elif action == "backup":
                    auto_rule_path = rules_dir / "auto_rule.mdc"
                    if not auto_rule_path.exists():
                        return {
                            "success": False,
                            "error": "auto_rule.mdc not found"
                        }
                    
                    backup_path = rules_dir / "auto_rule.mdc.backup"
                    with open(auto_rule_path, 'r', encoding='utf-8') as src:
                        content = src.read()
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(content)
                    
                    return {
                        "success": True,
                        "message": "Backup created successfully",
                        "backup_path": str(backup_path.relative_to(self.project_root))
                    }
                
                elif action == "restore":
                    backup_path = rules_dir / "auto_rule.mdc.backup"
                    if not backup_path.exists():
                        return {
                            "success": False,
                            "error": "Backup file not found"
                        }
                    
                    auto_rule_path = rules_dir / "auto_rule.mdc"
                    with open(backup_path, 'r', encoding='utf-8') as src:
                        content = src.read()
                    with open(auto_rule_path, 'w', encoding='utf-8') as dst:
                        dst.write(content)
                    
                    return {
                        "success": True,
                        "message": "Restored from backup successfully"
                    }
                
                elif action == "clean":
                    backup_files = list(rules_dir.rglob("*.backup"))
                    for backup_file in backup_files:
                        backup_file.unlink()
                    
                    return {
                        "success": True,
                        "message": f"Cleaned {len(backup_files)} backup files"
                    }
                
                elif action == "info":
                    if not rules_dir.exists():
                        return {
                            "success": True,
                            "info": {
                                "directory_exists": False,
                                "path": str(rules_dir.relative_to(self.project_root))
                            }
                        }
                    
                    all_files = list(rules_dir.rglob("*"))
                    mdc_files = list(rules_dir.rglob("*.mdc"))
                    backup_files = list(rules_dir.rglob("*.backup"))
                    
                    info = {
                        "directory_exists": True,
                        "path": str(rules_dir.relative_to(self.project_root)),
                        "total_files": len([f for f in all_files if f.is_file()]),
                        "mdc_files": len(mdc_files),
                        "backup_files": len(backup_files),
                        "auto_rule_exists": (rules_dir / "auto_rule.mdc").exists(),
                        "subdirectories": len([f for f in all_files if f.is_dir()])
                    }
                    
                    return {
                        "success": True,
                        "info": info
                    }
                
                else:
                    return {
                        "success": False,
                        "error": f"Unknown action: {action}. Available: list, backup, restore, clean, info"
                    }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Management operation failed: {str(e)}"
                }
        
        @mcp.tool()
        def regenerate_auto_rule(
            role: Annotated[Optional[str], Field(description="Target role for rule generation. Examples: senior_developer, task_planner, code_reviewer, security_engineer, qa_engineer")] = None,
            task_context: Annotated[Optional[Dict[str, Any]], Field(description="Specific task information with structure: {'id': '...', 'title': '...', 'description': '...', 'assignee': '...'}")] = None
        ) -> Dict[str, Any]:
            """🔄 AUTO-RULE REGENERATION ENGINE - Smart context generation for AI assistant

⭐ WHAT IT DOES: Automatically generates optimized auto_rule.mdc based on role and task context
📋 WHEN TO USE: Role switching, task context updates, AI behavior reset, context optimization
🎯 PERFECT FOR: Dynamic AI assistant configuration and context-aware rule generation

🧠 INTELLIGENT GENERATION:
• Role-Based Rules: Generates appropriate rules based on specified role
• Context Integration: Incorporates task-specific context and requirements
• Template Application: Uses proven rule templates and patterns
• Smart Defaults: Fills in missing information intelligently

📋 PARAMETERS (both optional):

👤 ROLE: Specify target role for rule generation
• Values: "senior_developer", "task_planner", "code_reviewer", etc.
• Effect: Generates role-specific context and behavioral rules
• Default: Uses "senior_developer" if not specified
• Example: role="security_engineer"

📝 TASK_CONTEXT: Provide specific task information
• Structure: {"id": "...", "title": "...", "description": "...", "assignee": "..."}
• Optional Fields: priority, details, status, due_date
• Smart Fallback: Creates generic context if not provided
• Integration: Pulls from active task if available

🎯 GENERATION ALGORITHM:
1. Analyzes provided role and task context
2. Selects appropriate rule templates
3. Customizes content for specific situation
4. Generates comprehensive auto_rule.mdc
5. Validates generated content quality

💡 SMART FEATURES:
• Template Synthesis: Combines multiple rule patterns
• Context Awareness: Adapts to project and task specifics
• Quality Assurance: Validates generated rules for completeness
• Immediate Effect: Generated rules take effect immediately

🎯 COMMON SCENARIOS:
• Role Change: regenerate_auto_rule(role="qa_engineer")
• Task Focus: Include specific task context for targeted rules
• Context Reset: Call without parameters for clean slate
• Workflow Optimization: Generate rules for specific project phases

🚀 PRODUCTIVITY BENEFITS:
• Instant Adaptation: AI behavior matches current needs
• Context Precision: Rules tailored to exact requirements
• Quality Consistency: Always generates well-structured rules
• Zero Manual Work: Eliminates need for manual rule writing
            """
            try:
                # If no specific context provided, create a generic one
                if not task_context:
                    task_context = {
                        "id": "manual",
                        "title": "Manual Rule Generation",
                        "description": "Manually triggered rule generation",
                        "status": "in_progress",
                        "priority": "medium",
                        "assignee": role or "senior_developer",
                        "details": "Rules generated manually via MCP tool"
                    }
                
                # Create a simple task-like object for the generator
                class SimpleTask:
                    def __init__(self, data):
                        self.id = type('TaskId', (), {'value': data['id']})()
                        self.title = data['title']
                        self.description = data['description']
                        self.assignee = data['assignee']
                        self.priority = type('Priority', (), {'value': data['priority']})()
                        self.details = data['details']
                        
                    def to_dict(self):
                        return {
                            'id': self.id.value,
                            'title': self.title,
                            'description': self.description,
                            'assignee': self.assignee,
                            'priority': self.priority.value,
                            'details': self.details,
                            'status': 'in_progress'
                        }
                
                task = SimpleTask(task_context)
                
                # Generate rules
                success = self._auto_rule_generator.generate_rules_for_task(task)
                
                if success:
                    return {
                        "success": True,
                        "message": "Auto rules regenerated successfully",
                        "role": role or task_context['assignee'],
                        "output_path": str((self.project_root / ".cursor" / "rules" / "auto_rule.mdc").relative_to(self.project_root))
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to regenerate auto rules"
                    }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Regeneration failed: {str(e)}"
                }
        
        @mcp.tool()
        def validate_tasks_json(
            file_path: Annotated[Optional[str], Field(description="Target tasks.json file to validate (default: .cursor/rules/tasks/tasks.json). Supports relative and absolute paths")] = None,
            output_format: Annotated[str, Field(description="Validation report detail level. Available: summary (default), detailed, json")] = "summary"
        ) -> Dict[str, Any]:
            """🔍 TASKS.JSON INTEGRITY VALIDATOR - Comprehensive task database health analysis

⭐ WHAT IT DOES: Deep analysis of tasks.json structure, data integrity, and schema compliance
📋 WHEN TO USE: After task modifications, troubleshooting data issues, pre-deployment checks
🎯 CRITICAL FOR: Data integrity, system reliability, preventing corruption in task management

🔬 COMPREHENSIVE VALIDATION:

📊 STRUCTURAL ANALYSIS:
• JSON Schema: Validates proper JSON structure and syntax
• Required Fields: Ensures all mandatory task properties exist
• Data Types: Verifies correct field types (strings, arrays, objects)
• Relationship Integrity: Validates task dependencies and subtask links

🎯 CONTENT VALIDATION:
• ID Uniqueness: Ensures no duplicate task identifiers
• Reference Integrity: Validates dependency and subtask references
• Value Constraints: Checks valid status, priority, and enum values
• Logical Consistency: Identifies contradictory or impossible states

📋 PARAMETERS:

📁 FILE_PATH (optional): Target file for validation
• Default: .cursor/rules/tasks/tasks.json (standard location)
• Custom: Specify alternate tasks.json file path
• Path Handling: Supports relative and absolute paths

📊 OUTPUT_FORMAT: Control validation report detail level
• "summary" (default): High-level overview with critical issues
• "detailed": Comprehensive analysis with specific errors
• "json": Machine-readable format for automation

🚨 ISSUE DETECTION:
• Missing Properties: Identifies incomplete task definitions
• Invalid References: Finds broken dependency or subtask links
• Data Corruption: Detects malformed or corrupted entries
• Schema Violations: Highlights structure and type mismatches

💡 QUALITY METRICS:
• Completeness Score: Percentage of properly formed tasks
• Integrity Health: Reference and relationship validation status
• Schema Compliance: Adherence to task management standards
• Performance Impact: File size and structure efficiency

🎯 USE CASES:
• Pre-Deployment: Validate before system updates
• Troubleshooting: Diagnose task management issues
• Data Migration: Verify after import/export operations
• Quality Assurance: Regular health checks of task database
• Integration Testing: Ensure compatibility with external systems

🔧 DEVELOPER BENEFITS:
• Early Problem Detection: Catch issues before they cause failures
• Data Quality Assurance: Maintain high-quality task database
• Debug Support: Detailed error information for quick fixes
• Automation Ready: JSON output enables automated validation
            """
            try:
                # Import the validator class
                import sys
                import importlib.util
                
                # Load the tasks validator from the tools directory
                validator_path = self.project_root / ".cursor" / "rules" / "tools" / "tasks_validator.py"
                
                if not validator_path.exists():
                    return {
                        "success": False,
                        "error": f"Tasks validator not found: {validator_path}"
                    }
                
                # Load the validator module
                spec = importlib.util.spec_from_file_location("tasks_validator", validator_path)
                validator_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(validator_module)
                
                # Create validator instance
                validator = validator_module.TasksValidator(file_path)
                
                # Run validation
                result = validator.validate()
                
                if output_format == "json":
                    return {
                        "success": True,
                        "validation_result": result
                    }
                elif output_format == "detailed":
                    return {
                        "success": True,
                        "file_path": result["file_path"],
                        "file_exists": result["file_exists"],
                        "validation_passed": result["validation_passed"],
                        "total_issues": result["total_issues"],
                        "summary": result["summary"],
                        "errors": result["errors"],
                        "warnings": result["warnings"],
                        "missing_properties": result["missing_properties"],
                        "recommendations": result["recommendations"]
                    }
                else:  # summary format
                    status = "✅ VALID" if result["validation_passed"] else "❌ INVALID"
                    issues_summary = f"Errors: {result['summary']['errors']}, Warnings: {result['summary']['warnings']}, Missing: {result['summary']['missing_properties']}"
                    
                    return {
                        "success": True,
                        "file_path": result["file_path"],
                        "status": status,
                        "validation_passed": result["validation_passed"],
                        "total_issues": result["total_issues"],
                        "issues_summary": issues_summary,
                        "critical_errors": result["errors"][:3] if result["errors"] else [],
                        "recommendations": result["recommendations"][:2] if result["recommendations"] else []
                    }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Validation failed: {str(e)}"
                } 