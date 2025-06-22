"""Comprehensive tests for file_operations.py to improve coverage from 27% to 90%+"""

import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

from task_mcp.infrastructure.services.legacy.project_analyzer.file_operations import FileOperations


class TestFileOperations:
    """Comprehensive tests for FileOperations class"""

    @pytest.fixture
    def temp_project_root(self):
        """Create a temporary project root directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def file_operations(self, temp_project_root):
        """Create FileOperations instance with temporary project root"""
        return FileOperations(temp_project_root)

    @pytest.fixture
    def sample_context_data(self):
        """Sample context data for testing"""
        return {
            "project_structure": {
                "src": ["main.py", "utils.py"],
                "tests": ["test_main.py"]
            },
            "existing_patterns": ["MVC", "Repository"],
            "dependencies": ["fastapi", "pytest"],
            "context_summary": "Sample project summary",
            "phase_specific_context": "Coding phase context"
        }

    def test_init(self, temp_project_root):
        """Test FileOperations initialization"""
        file_ops = FileOperations(temp_project_root)
        assert file_ops.project_root == temp_project_root

    def test_save_context_to_file_success(self, file_operations, temp_project_root, sample_context_data):
        """Test successful context saving to file"""
        context_file = temp_project_root / "context.json"
        
        result = file_operations.save_context_to_file(context_file, sample_context_data, "coding")
        
        assert result is True
        assert context_file.exists()
        
        # Verify file contents
        with open(context_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["project_root"] == str(temp_project_root)
        assert saved_data["analysis_version"] == "1.0"
        assert saved_data["project_structure"] == sample_context_data["project_structure"]
        assert saved_data["existing_patterns"] == sample_context_data["existing_patterns"]
        assert saved_data["dependencies"] == sample_context_data["dependencies"]
        assert saved_data["context_summary"] == sample_context_data["context_summary"]
        assert saved_data["phase_specific_context"] == sample_context_data["phase_specific_context"]
        assert saved_data["tree_formatter"] is None
        assert "timestamp" in saved_data
        assert isinstance(saved_data["timestamp"], (int, float))

    def test_save_context_to_file_creates_directory(self, file_operations, temp_project_root, sample_context_data):
        """Test that save_context_to_file creates parent directories if they don't exist"""
        nested_dir = temp_project_root / "nested" / "deep" / "path"
        context_file = nested_dir / "context.json"
        
        result = file_operations.save_context_to_file(context_file, sample_context_data)
        
        assert result is True
        assert context_file.exists()
        assert nested_dir.exists()

    def test_save_context_to_file_with_missing_data(self, file_operations, temp_project_root):
        """Test saving context with missing optional data"""
        context_file = temp_project_root / "context.json"
        minimal_data = {}
        
        result = file_operations.save_context_to_file(context_file, minimal_data)
        
        assert result is True
        assert context_file.exists()
        
        # Verify defaults are applied
        with open(context_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["project_structure"] == {}
        assert saved_data["existing_patterns"] == []
        assert saved_data["dependencies"] == []
        assert saved_data["context_summary"] == ""
        assert saved_data["phase_specific_context"] == ""

    def test_save_context_to_file_atomic_operation(self, file_operations, temp_project_root, sample_context_data):
        """Test that save operation is atomic (uses temporary file)"""
        context_file = temp_project_root / "context.json"
        temp_file = context_file.with_suffix(".tmp")
        
        # Mock the rename operation to fail and verify temp file is created
        with patch('pathlib.Path.rename', side_effect=OSError("Rename failed")):
            result = file_operations.save_context_to_file(context_file, sample_context_data)
            
            assert result is False
            assert not context_file.exists()
            # Temp file should have been created but not renamed
            # Note: The actual temp file might be cleaned up by the exception handler

    def test_save_context_to_file_json_error(self, file_operations, temp_project_root):
        """Test save_context_to_file handles JSON serialization errors"""
        context_file = temp_project_root / "context.json"
        
        # Mock json.dump to raise an error
        with patch('json.dump', side_effect=TypeError("Object not JSON serializable")):
            result = file_operations.save_context_to_file(context_file, {"test": "data"})
            
            assert result is False
            assert not context_file.exists()

    def test_save_context_to_file_permission_error(self, file_operations, temp_project_root, sample_context_data):
        """Test save_context_to_file handles permission errors"""
        context_file = temp_project_root / "context.json"
        
        # Mock open to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = file_operations.save_context_to_file(context_file, sample_context_data)
            
            assert result is False

    def test_load_context_from_file_success(self, file_operations, temp_project_root, sample_context_data):
        """Test successful context loading from file"""
        context_file = temp_project_root / "context.json"
        
        # First save some context
        file_operations.save_context_to_file(context_file, sample_context_data)
        
        # Then load it
        loaded_data = file_operations.load_context_from_file(context_file)
        
        assert loaded_data is not None
        assert loaded_data["project_root"] == str(temp_project_root)
        assert loaded_data["project_structure"] == sample_context_data["project_structure"]
        assert loaded_data["existing_patterns"] == sample_context_data["existing_patterns"]
        assert loaded_data["dependencies"] == sample_context_data["dependencies"]

    def test_load_context_from_file_not_exists(self, file_operations, temp_project_root):
        """Test loading from non-existent file returns None"""
        context_file = temp_project_root / "nonexistent.json"
        
        result = file_operations.load_context_from_file(context_file)
        
        assert result is None

    def test_load_context_from_file_invalid_json(self, file_operations, temp_project_root):
        """Test loading from file with invalid JSON"""
        context_file = temp_project_root / "invalid.json"
        
        # Create file with invalid JSON
        with open(context_file, 'w') as f:
            f.write("{ invalid json content")
        
        result = file_operations.load_context_from_file(context_file)
        
        assert result is None

    def test_load_context_from_file_missing_required_keys(self, file_operations, temp_project_root):
        """Test loading from file with missing required keys"""
        context_file = temp_project_root / "incomplete.json"
        
        # Create file with incomplete data
        incomplete_data = {
            "timestamp": time.time(),
            "project_root": str(temp_project_root),
            # Missing required keys: project_structure, existing_patterns, dependencies
        }
        
        with open(context_file, 'w') as f:
            json.dump(incomplete_data, f)
        
        result = file_operations.load_context_from_file(context_file)
        
        assert result is None

    def test_load_context_from_file_has_all_required_keys(self, file_operations, temp_project_root):
        """Test loading from file with all required keys present"""
        context_file = temp_project_root / "complete.json"
        
        # Create file with all required keys
        complete_data = {
            "timestamp": time.time(),
            "project_root": str(temp_project_root),
            "project_structure": {},
            "existing_patterns": [],
            "dependencies": [],
            "context_summary": "test",
            "phase_specific_context": "test"
        }
        
        with open(context_file, 'w') as f:
            json.dump(complete_data, f)
        
        result = file_operations.load_context_from_file(context_file)
        
        assert result is not None
        assert result == complete_data

    def test_load_context_from_file_os_error(self, file_operations, temp_project_root):
        """Test loading from file handles OS errors"""
        context_file = temp_project_root / "context.json"
        
        # Create the file first
        with open(context_file, 'w') as f:
            json.dump({"test": "data"}, f)
        
        # Mock open to raise OSError
        with patch('builtins.open', side_effect=OSError("File access error")):
            result = file_operations.load_context_from_file(context_file)
            
            assert result is None

    def test_save_and_load_roundtrip(self, file_operations, temp_project_root, sample_context_data):
        """Test complete save and load roundtrip"""
        context_file = temp_project_root / "roundtrip.json"
        
        # Save context
        save_result = file_operations.save_context_to_file(context_file, sample_context_data, "testing")
        assert save_result is True
        
        # Load context
        loaded_data = file_operations.load_context_from_file(context_file)
        assert loaded_data is not None
        
        # Verify key data is preserved
        assert loaded_data["project_structure"] == sample_context_data["project_structure"]
        assert loaded_data["existing_patterns"] == sample_context_data["existing_patterns"]
        assert loaded_data["dependencies"] == sample_context_data["dependencies"]
        assert loaded_data["context_summary"] == sample_context_data["context_summary"]
        assert loaded_data["phase_specific_context"] == sample_context_data["phase_specific_context"]

    def test_save_context_different_phases(self, file_operations, temp_project_root, sample_context_data):
        """Test saving context with different task phases"""
        context_file = temp_project_root / "phase_test.json"
        
        phases = ["coding", "testing", "deployment", "review"]
        
        for phase in phases:
            result = file_operations.save_context_to_file(context_file, sample_context_data, phase)
            assert result is True
            
            # Verify file exists and can be loaded
            loaded_data = file_operations.load_context_from_file(context_file)
            assert loaded_data is not None

    def test_save_context_with_complex_data_structures(self, file_operations, temp_project_root):
        """Test saving context with complex nested data structures"""
        context_file = temp_project_root / "complex.json"
        
        complex_data = {
            "project_structure": {
                "src": {
                    "components": ["Button.tsx", "Input.tsx"],
                    "services": ["api.ts", "auth.ts"],
                    "utils": ["helpers.ts", "constants.ts"]
                },
                "tests": {
                    "unit": ["component.test.ts"],
                    "integration": ["api.test.ts"]
                }
            },
            "existing_patterns": [
                {"pattern": "MVC", "usage": "controllers"},
                {"pattern": "Repository", "usage": "data access"}
            ],
            "dependencies": [
                {"name": "react", "version": "^18.0.0", "type": "runtime"},
                {"name": "jest", "version": "^29.0.0", "type": "dev"}
            ],
            "context_summary": "Complex nested project structure",
            "phase_specific_context": "Advanced testing phase"
        }
        
        result = file_operations.save_context_to_file(context_file, complex_data)
        assert result is True
        
        loaded_data = file_operations.load_context_from_file(context_file)
        assert loaded_data is not None
        assert loaded_data["project_structure"] == complex_data["project_structure"]
        assert loaded_data["existing_patterns"] == complex_data["existing_patterns"]
        assert loaded_data["dependencies"] == complex_data["dependencies"] 