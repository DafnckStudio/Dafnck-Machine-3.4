#!/usr/bin/env python3
"""
Dual Mode Test Runner
Runs tests for both stdio and HTTP modes to verify functionality
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def run_tests_with_mode(mode: str):
    """Run tests with a specific mode configuration"""
    print(f"\n{'='*60}")
    print(f"RUNNING TESTS IN {mode.upper()} MODE")
    print(f"{'='*60}")
    
    # Set environment for the mode
    env = os.environ.copy()
    
    if mode == "http":
        env["FASTMCP_TRANSPORT"] = "streamable-http"
        env["CURSOR_RULES_DIR"] = "/data/rules"
        print("Environment set for HTTP mode (Docker simulation)")
    else:
        # Clear HTTP mode environment variables
        for var in ["FASTMCP_TRANSPORT", "CURSOR_RULES_DIR"]:
            if var in env:
                del env[var]
        print("Environment set for stdio mode (local development)")
    
    # Run the tests
    test_files = [
        "test_dual_mode_configuration.py",
        "test_manage_rule_integration.py"
    ]
    
    for test_file in test_files:
        print(f"\nRunning {test_file}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                str(Path(__file__).parent / test_file),
                "-v", "--tb=short"
            ], env=env, capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                print(f"✅ {test_file} PASSED")
            else:
                print(f"❌ {test_file} FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")


def run_quick_functionality_test():
    """Run a quick test to verify basic functionality"""
    print(f"\n{'='*60}")
    print("QUICK FUNCTIONALITY TEST")
    print(f"{'='*60}")
    
    try:
        from fastmcp.dual_mode_config import (
            dual_mode_config,
            get_runtime_mode,
            get_rules_directory,
            is_http_mode,
            is_stdio_mode
        )
        
        print(f"✅ Dual mode config imported successfully")
        print(f"Runtime mode: {get_runtime_mode()}")
        print(f"Rules directory: {get_rules_directory()}")
        print(f"Is HTTP mode: {is_http_mode()}")
        print(f"Is stdio mode: {is_stdio_mode()}")
        
        # Test CursorRulesTools integration
        from fastmcp.task_management.interface.cursor_rules_tools import CursorRulesTools
        
        cursor_tools = CursorRulesTools()
        rules_dir = cursor_tools._get_rules_directory_from_settings()
        print(f"✅ CursorRulesTools integration working")
        print(f"Resolved rules directory: {rules_dir}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This is expected if dependencies are not installed")
    except Exception as e:
        print(f"❌ Functionality test error: {e}")


def main():
    """Main test runner"""
    print("Dual Mode Configuration Test Suite")
    print("Testing stdio (local) and HTTP (Docker) modes")
    
    # Run quick functionality test first
    run_quick_functionality_test()
    
    # Run tests in both modes
    run_tests_with_mode("stdio")
    run_tests_with_mode("http")
    
    print(f"\n{'='*60}")
    print("TEST SUITE COMPLETED")
    print(f"{'='*60}")
    print("\nNote: Some tests may require dependencies to be installed.")
    print("Install with: pip install -e .")


if __name__ == "__main__":
    main()