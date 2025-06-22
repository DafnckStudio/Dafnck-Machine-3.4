#!/usr/bin/env python3
"""Simple script to run tests and check coverage"""

import subprocess
import sys
import os

def run_command(cmd, env=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120, env=env)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"

def main():
    """Main function"""
    project_root = '/home/daihungpham/agentic-project'
    
    # Change to the correct directory
    cursor_agent_dir = os.path.join(project_root, 'cursor_agent')
    os.chdir(cursor_agent_dir)
    
    print("Running tests with coverage...")
    
    # Set PYTHONPATH for the subprocess
    env = os.environ.copy()
    env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')

    # Run tests with coverage
    cmd = "uv run pytest tests/ --cov=src --cov-report=term-missing --tb=short"
    returncode, stdout, stderr = run_command(cmd, env=env)
    
    print("STDOUT:")
    print(stdout)
    print("\nSTDERR:")
    print(stderr)
    print(f"\nReturn code: {returncode}")
    
    return returncode

if __name__ == "__main__":
    sys.exit(main()) 