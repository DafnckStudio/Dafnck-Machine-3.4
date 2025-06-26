"""
Pytest plugin for automatic test data cleanup.

This plugin ensures that test projects and data are cleaned up after test sessions,
even if tests fail or are interrupted.
"""

import subprocess
import sys
import atexit
from pathlib import Path
import pytest


class TestDataCleanupPlugin:
    """Plugin to handle test data cleanup."""
    
    def __init__(self):
        self.cleanup_registered = False
        self.cleanup_script_path = None
        
    def pytest_configure(self, config):
        """Configure the plugin and register cleanup."""
        # Find the cleanup script
        self.cleanup_script_path = Path(__file__).parent / "cleanup_test_data.py"
        
        # Register cleanup to run at exit (even if interrupted)
        if not self.cleanup_registered:
            atexit.register(self._run_cleanup)
            self.cleanup_registered = True
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Run cleanup after test session finishes."""
        self._run_cleanup()
    
    def _run_cleanup(self):
        """Execute the cleanup script."""
        try:
            if self.cleanup_script_path and self.cleanup_script_path.exists():
                print("\n🧹 Running test data cleanup...")
                result = subprocess.run(
                    [sys.executable, str(self.cleanup_script_path)], 
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0:
                    print("✅ Test data cleanup completed successfully")
                    if result.stdout:
                        # Only print non-empty, meaningful output
                        lines = [line for line in result.stdout.split('\n') if line.strip()]
                        if len(lines) > 2:  # More than just start/end messages
                            print(result.stdout)
                else:
                    print(f"⚠️  Test data cleanup had issues (exit code: {result.returncode})")
                    if result.stderr:
                        print(f"Error: {result.stderr}")
                    if result.stdout:
                        print(f"Output: {result.stdout}")
            else:
                print(f"⚠️  Cleanup script not found at: {self.cleanup_script_path}")
        except subprocess.TimeoutExpired:
            print("⚠️  Test data cleanup timed out (30s)")
        except Exception as e:
            print(f"❌ Error during test data cleanup: {e}")


# Create plugin instance
cleanup_plugin = TestDataCleanupPlugin()


def pytest_configure(config):
    """Hook to configure the plugin."""
    cleanup_plugin.pytest_configure(config)


def pytest_sessionfinish(session, exitstatus):
    """Hook to run cleanup after session finishes."""
    cleanup_plugin.pytest_sessionfinish(session, exitstatus) 