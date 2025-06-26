#!/usr/bin/env python3
"""
Demonstration of Complete Test Data Isolation System

This script demonstrates how the new test isolation system ensures that:
1. All test data uses .test.json and .test.mdc files
2. Production data is never touched during testing
3. Test cleanup only affects test files
4. Multiple test environments are completely isolated

Run this script to see the system in action.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add test directory to path
sys.path.insert(0, str(Path(__file__).parent))

from test_environment_config import (
    isolated_test_environment, 
    is_test_file, 
    cleanup_test_files_only,
    TestEnvironmentConfig
)


def demo_isolated_environments():
    """Demonstrate isolated test environments"""
    print("🧪 DEMO 1: Isolated Test Environments")
    print("=" * 50)
    
    # Create multiple isolated environments
    with isolated_test_environment(test_id="env_alpha") as config_alpha:
        with isolated_test_environment(test_id="env_beta") as config_beta:
            
            print(f"📁 Environment Alpha: {config_alpha.temp_dir}")
            print(f"📁 Environment Beta:  {config_beta.temp_dir}")
            print()
            
            # Add different projects to each environment
            config_alpha.add_test_project("project_alpha", "Alpha Test Project")
            config_beta.add_test_project("project_beta", "Beta Test Project")
            
            # Verify isolation
            with open(config_alpha.test_files["projects"], 'r') as f:
                alpha_data = json.load(f)
            
            with open(config_beta.test_files["projects"], 'r') as f:
                beta_data = json.load(f)
            
            print("✅ Environment Alpha contains:")
            for project_id in alpha_data:
                print(f"   - {project_id} (test_id: {alpha_data[project_id]['test_id']})")
            
            print("✅ Environment Beta contains:")
            for project_id in beta_data:
                print(f"   - {project_id} (test_id: {beta_data[project_id]['test_id']})")
            
            # Verify complete isolation
            assert "project_alpha" in alpha_data
            assert "project_beta" not in alpha_data
            assert "project_beta" in beta_data
            assert "project_alpha" not in beta_data
            
            print("🛡️  Environments are completely isolated!")
            print()
    
    print("🧹 Both environments cleaned up automatically")
    print()


def demo_file_naming_convention():
    """Demonstrate .test.json file naming convention"""
    print("🧪 DEMO 2: Test File Naming Convention")
    print("=" * 50)
    
    with isolated_test_environment(test_id="naming_demo") as config:
        print("📁 Test files created:")
        for file_type, file_path in config.test_files.items():
            print(f"   {file_type}: {file_path.name}")
            assert file_path.exists(), f"File should exist: {file_path}"
        
        # Verify all files follow naming convention
        assert config.test_files["projects"].name == "projects.test.json"
        assert config.test_files["tasks"].name == "tasks.test.json"
        assert config.test_files["auto_rule"].name == "auto_rule.test.mdc"
        
        print("✅ All test files follow .test.json/.test.mdc naming convention")
        print()


def demo_safe_file_identification():
    """Demonstrate safe file identification for cleanup"""
    print("🧪 DEMO 3: Safe File Identification")
    print("=" * 50)
    
    # Test files that should be identified as test files
    test_files = [
        Path("projects.test.json"),
        Path("tasks.test.json"),
        Path("auto_rule.test.mdc"),
        Path("test_data.json"),
        Path("e2e_results.json"),
        Path("migration_test_config.json")
    ]
    
    # Production files that should NOT be identified as test files
    production_files = [
        Path("projects.json"),
        Path("tasks.json"),
        Path("auto_rule.mdc"),
        Path("config.json"),
        Path("data.json"),
        Path("important_data.json")
    ]
    
    print("✅ Files correctly identified as TEST files:")
    for file_path in test_files:
        if is_test_file(file_path):
            print(f"   ✓ {file_path.name}")
        else:
            print(f"   ❌ {file_path.name} (ERROR: should be identified as test file)")
    
    print("\n🛡️  Files correctly identified as PRODUCTION files (safe from cleanup):")
    for file_path in production_files:
        if not is_test_file(file_path):
            print(f"   ✓ {file_path.name}")
        else:
            print(f"   ❌ {file_path.name} (ERROR: should NOT be identified as test file)")
    
    print()


def demo_production_data_protection():
    """Demonstrate that production data is never touched"""
    print("🧪 DEMO 4: Production Data Protection")
    print("=" * 50)
    
    # Check production projects.json
    production_projects_file = Path(".cursor/rules/brain/projects.json")
    
    if production_projects_file.exists():
        with open(production_projects_file, 'r') as f:
            production_data = json.load(f)
        
        print(f"📁 Production projects.json contains {len(production_data)} project(s):")
        for project_id in production_data:
            print(f"   - {project_id}")
        
        # Create test environment and add test data
        with isolated_test_environment(test_id="protection_test") as config:
            config.add_test_project("test_project_should_not_affect_production", "Test Project")
            
            # Verify production data is unchanged
            with open(production_projects_file, 'r') as f:
                production_data_after = json.load(f)
            
            assert production_data == production_data_after, "Production data was modified!"
            assert "test_project_should_not_affect_production" not in production_data_after
            
            print("🛡️  Production data completely unaffected by test operations")
    else:
        print("ℹ️  No production projects.json found (this is normal in some environments)")
    
    print()


def demo_cleanup_safety():
    """Demonstrate that cleanup only affects test files"""
    print("🧪 DEMO 5: Cleanup Safety")
    print("=" * 50)
    
    # Create temporary directory with mixed files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files (should be cleaned)
        test_files = [
            temp_path / "projects.test.json",
            temp_path / "tasks.test.json",
            temp_path / "auto_rule.test.mdc",
            temp_path / "test_data.json"
        ]
        
        # Create production-like files (should NOT be cleaned)
        production_files = [
            temp_path / "projects.json",
            temp_path / "tasks.json",
            temp_path / "auto_rule.mdc",
            temp_path / "important_config.json"
        ]
        
        # Create all files
        for file_path in test_files + production_files:
            file_path.write_text(f"Content of {file_path.name}")
        
        print(f"📁 Created {len(test_files)} test files and {len(production_files)} production files")
        
        # Run cleanup
        cleaned_count = cleanup_test_files_only(temp_path)
        
        # Verify results
        remaining_files = list(temp_path.iterdir())
        remaining_names = [f.name for f in remaining_files]
        
        print(f"🧹 Cleanup removed {cleaned_count} files")
        print(f"📁 Remaining files: {len(remaining_files)}")
        
        for file_path in production_files:
            if file_path.exists():
                print(f"   ✅ Protected: {file_path.name}")
            else:
                print(f"   ❌ ERROR: Production file was deleted: {file_path.name}")
        
        for file_path in test_files:
            if not file_path.exists():
                print(f"   🧹 Cleaned: {file_path.name}")
            else:
                print(f"   ⚠️  Test file not cleaned: {file_path.name}")
        
        # Verify all production files are safe
        for file_path in production_files:
            assert file_path.exists(), f"Production file was incorrectly deleted: {file_path}"
        
        print("🛡️  All production files protected, only test files cleaned")
    
    print()


def main():
    """Run all demonstrations"""
    print("🎯 DhafnckMCP Test Data Isolation System Demonstration")
    print("=" * 60)
    print("This demo shows how the new system ensures complete isolation")
    print("between test data and production data using .test.json files.")
    print("=" * 60)
    print()
    
    try:
        demo_isolated_environments()
        demo_file_naming_convention()
        demo_safe_file_identification()
        demo_production_data_protection()
        demo_cleanup_safety()
        
        print("🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Test environments are completely isolated")
        print("✅ All test files use .test.json/.test.mdc naming")
        print("✅ Production data is never touched")
        print("✅ Cleanup only affects test files")
        print("✅ Multiple environments work independently")
        print("🛡️  PRODUCTION DATA IS COMPLETELY SAFE")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"❌ DEMONSTRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main()) 