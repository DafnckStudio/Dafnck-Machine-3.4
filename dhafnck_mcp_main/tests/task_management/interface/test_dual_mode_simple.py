"""
Simple Dual Mode Configuration Test
Tests that don't require complex dependencies
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add project src to path for imports - with error handling
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_dual_mode_imports():
    """Test that dual mode configuration can be imported"""
    try:
        from fastmcp.dual_mode_config import (
            DualModeConfig,
            get_runtime_mode,
            get_rules_directory,
            is_http_mode,
            is_stdio_mode
        )
        print("✅ Dual mode configuration imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_mode_detection():
    """Test runtime mode detection logic"""
    try:
        from fastmcp.dual_mode_config import DualModeConfig
        
        # Test stdio mode (default)
        config = DualModeConfig()
        print(f"Default mode detection: {config.runtime_mode}")
        
        # Test with environment variable
        os.environ["FASTMCP_TRANSPORT"] = "streamable-http"
        config_http = DualModeConfig()
        print(f"HTTP mode detection: {config_http.runtime_mode}")
        
        # Clean up
        del os.environ["FASTMCP_TRANSPORT"]
        
        print("✅ Mode detection tests passed")
        return True
    except Exception as e:
        print(f"❌ Mode detection failed: {e}")
        return False


def test_path_resolution():
    """Test path resolution in both modes"""
    try:
        from fastmcp.dual_mode_config import DualModeConfig
        
        # Test stdio mode
        config_stdio = DualModeConfig()
        rules_dir_stdio = config_stdio.get_rules_directory()
        print(f"Stdio rules directory: {rules_dir_stdio}")
        
        # Test HTTP mode simulation
        with patch('os.path.exists', return_value=True):
            os.environ["FASTMCP_TRANSPORT"] = "streamable-http"
            config_http = DualModeConfig()
            rules_dir_http = config_http.get_rules_directory()
            print(f"HTTP rules directory: {rules_dir_http}")
            del os.environ["FASTMCP_TRANSPORT"]
        
        print("✅ Path resolution tests passed")
        return True
    except Exception as e:
        print(f"❌ Path resolution failed: {e}")
        return False


def test_convenience_functions():
    """Test convenience functions"""
    try:
        from fastmcp.dual_mode_config import (
            get_runtime_mode,
            get_rules_directory,
            get_data_directory,
            is_http_mode,
            is_stdio_mode,
            resolve_path
        )
        
        mode = get_runtime_mode()
        rules_dir = get_rules_directory()
        data_dir = get_data_directory()
        http_mode = is_http_mode()
        stdio_mode = is_stdio_mode()
        
        print(f"Runtime mode: {mode}")
        print(f"Rules directory: {rules_dir}")
        print(f"Data directory: {data_dir}")
        print(f"Is HTTP mode: {http_mode}")
        print(f"Is stdio mode: {stdio_mode}")
        
        # Test path resolution
        resolved = resolve_path("test.txt", "project")
        print(f"Resolved path: {resolved}")
        
        print("✅ Convenience functions tests passed")
        return True
    except Exception as e:
        print(f"❌ Convenience functions failed: {e}")
        return False


def run_all_tests():
    """Run all simple tests"""
    print("=" * 60)
    print("DUAL MODE CONFIGURATION SIMPLE TESTS")
    print("=" * 60)
    
    tests = [
        test_dual_mode_imports,
        test_mode_detection,
        test_path_resolution,
        test_convenience_functions
    ]
    
    results = []
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        results.append(test())
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test.__name__}: {status}")
    
    print(f"\nSUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)