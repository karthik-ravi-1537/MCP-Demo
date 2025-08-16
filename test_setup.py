#!/usr/bin/env python3
"""
Quick setup verification for MCP Demo Project.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all core modules can be imported."""
    try:
        # Test core imports
        from mcp_servers.base import BaseMCPServer
        from mcp_servers.calculator_server import CalculatorServer
        from mcp_servers.file_server import FileSystemServer
        from server.app import app
        from tutorials.models import Tutorial
        print("✅ All core imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality."""
    try:
        from mcp_servers.calculator_server import CalculatorServer
        
        # Test calculator server initialization
        calc_server = CalculatorServer()
        assert calc_server.name == "calculator"
        
        print("✅ Basic functionality test passed")
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_environment():
    """Test environment setup."""
    try:
        # Check if .env.example exists
        env_example = Path(".env.example")
        if env_example.exists():
            print("✅ Environment template found")
        else:
            print("⚠️  .env.example not found")
        
        # Check if required directories exist
        required_dirs = ["mcp_servers", "server", "tutorials", "tests"]
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                print(f"✅ {dir_name}/ directory found")
            else:
                print(f"❌ {dir_name}/ directory missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def main():
    """Run all setup tests."""
    print("🚀 MCP Demo Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Functionality Test", test_basic_functionality),
        ("Environment Test", test_environment),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All tests passed! MCP Demo is ready to use.")
        print("\nNext steps:")
        print("1. Start the server: python cli.py server")
        print("2. Open http://localhost:8000 in your browser")
        print("3. Follow the interactive tutorials!")
        return 0
    else:
        print("❌ Some tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())