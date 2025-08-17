#!/usr/bin/env python3
"""
Enhanced Setup Verification for MCP Demo Project
===============================================

Comprehensive verification script to ensure MCP Demo is properly set up
and ready to use. Tests all components and provides helpful guidance.

Run with: python verify_setup.py
"""

import sys
import tempfile
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class SetupVerifier:
    """Comprehensive setup verification for MCP Demo."""

    def __init__(self):
        self.results: list[tuple[str, bool, str]] = []
        self.project_root = Path(__file__).parent

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log a test result."""
        self.results.append((test_name, success, message))
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")

    def test_python_version(self) -> bool:
        """Test Python version compatibility."""
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 8:
                self.log_result(
                    "Python Version", True, f"Python {version.major}.{version.minor}.{version.micro} (✓ Compatible)"
                )
                return True
            else:
                self.log_result(
                    "Python Version", False, f"Python {version.major}.{version.minor}.{version.micro} (Requires 3.8+)"
                )
                return False
        except Exception as e:
            self.log_result("Python Version", False, f"Error checking version: {e}")
            return False

    def test_dependencies(self) -> bool:
        """Test that all required dependencies are installed."""
        required_packages = [
            ("fastapi", "FastAPI web framework"),
            ("uvicorn", "ASGI server"),
            ("pydantic", "Data validation"),
            ("jinja2", "Template engine"),
            ("click", "CLI framework"),
            ("aiofiles", "Async file operations"),
            ("httpx", "HTTP client"),
        ]

        all_success = True

        for package, description in required_packages:
            try:
                __import__(package)
                self.log_result(f"Dependency: {package}", True, description)
            except ImportError:
                self.log_result(f"Dependency: {package}", False, f"Missing {description}")
                all_success = False

        return all_success

    def test_project_structure(self) -> bool:
        """Test that all required project directories exist."""
        required_structure = {
            "mcp_servers": "MCP server implementations",
            "server": "Web application server",
            "tutorials": "Tutorial content",
            "tests": "Test suite",
            "server/api": "API endpoints",
            "server/templates": "Web templates",
        }

        all_success = True

        for path, description in required_structure.items():
            full_path = self.project_root / path
            if full_path.exists():
                self.log_result(f"Directory: {path}", True, description)
            else:
                self.log_result(f"Directory: {path}", False, f"Missing {description}")
                all_success = False

        return all_success

    def test_core_imports(self) -> bool:
        """Test that core modules can be imported."""
        core_imports = [
            ("mcp_servers.base", "Base MCP server"),
            ("mcp_servers.calculator_server", "Calculator server"),
            ("mcp_servers.file_server", "File system server"),
            ("server.app", "Web application"),
            ("tutorials.models", "Tutorial models"),
        ]

        all_success = True

        for module, description in core_imports:
            try:
                __import__(module)
                self.log_result(f"Import: {module}", True, description)
            except ImportError as e:
                self.log_result(f"Import: {module}", False, f"Failed: {e}")
                all_success = False

        return all_success

    def test_calculator_server(self) -> bool:
        """Test calculator server functionality."""
        try:
            from mcp_servers.calculator_server import CalculatorServer

            calc = CalculatorServer()

            # Test basic operations
            tests = [
                (lambda: calc.add(2, 3), 5, "Addition"),
                (lambda: calc.subtract(10, 4), 6, "Subtraction"),
                (lambda: calc.multiply(3, 7), 21, "Multiplication"),
                (lambda: calc.divide(15, 3), 5.0, "Division"),
                (lambda: calc.power(2, 3), 8.0, "Power"),
                (lambda: calc.sqrt(16), 4.0, "Square root"),
                (lambda: calc.factorial(4), 24, "Factorial"),
            ]

            all_success = True
            for test_func, expected, operation in tests:
                try:
                    result = test_func()
                    if result == expected:
                        self.log_result(f"Calculator: {operation}", True, f"{result}")
                    else:
                        self.log_result(f"Calculator: {operation}", False, f"Expected {expected}, got {result}")
                        all_success = False
                except Exception as e:
                    self.log_result(f"Calculator: {operation}", False, f"Error: {e}")
                    all_success = False

            # Test error handling
            try:
                calc.divide(1, 0)
                self.log_result("Calculator: Error handling", False, "Division by zero should fail")
                all_success = False
            except ValueError:
                self.log_result("Calculator: Error handling", True, "Division by zero properly handled")
            except Exception as e:
                self.log_result("Calculator: Error handling", False, f"Unexpected error: {e}")
                all_success = False

            return all_success

        except Exception as e:
            self.log_result("Calculator Server", False, f"Failed to initialize: {e}")
            return False

    def test_file_server(self) -> bool:
        """Test file server functionality."""
        try:
            from mcp_servers.file_server import FileSystemServer

            with tempfile.TemporaryDirectory() as temp_dir:
                file_server = FileSystemServer(base_dir=temp_dir)

                # Test file operations
                test_content = "Hello, MCP!"
                test_file = "test.txt"

                try:
                    # Write file
                    file_server.write_file(test_file, test_content)
                    self.log_result("File Server: Write", True, "File created successfully")

                    # Read file
                    content = file_server.read_file(test_file)
                    if content == test_content:
                        self.log_result("File Server: Read", True, "File content matches")
                    else:
                        self.log_result("File Server: Read", False, "Content mismatch")
                        return False

                    # List directory
                    files = file_server.list_directory(".")
                    if any(f["path"] == test_file for f in files):
                        self.log_result("File Server: List", True, "File found in listing")
                    else:
                        self.log_result("File Server: List", False, "File not found in listing")
                        return False

                    # Check file exists
                    if file_server.path_exists(test_file):
                        self.log_result("File Server: Exists", True, "File existence confirmed")
                    else:
                        self.log_result("File Server: Exists", False, "File existence check failed")
                        return False

                    # Test security (path traversal)
                    try:
                        file_server.read_file("../../../etc/passwd")
                        self.log_result("File Server: Security", False, "Path traversal not blocked")
                        return False
                    except Exception:
                        self.log_result("File Server: Security", True, "Path traversal properly blocked")

                    return True

                except Exception as e:
                    self.log_result("File Server: Operations", False, f"Error: {e}")
                    return False

        except Exception as e:
            self.log_result("File Server", False, f"Failed to initialize: {e}")
            return False

    def test_web_server_config(self) -> bool:
        """Test web server configuration."""
        try:
            from server.app import create_app

            app = create_app()
            self.log_result("Web Server: Config", True, "FastAPI app created successfully")

            # Check routes
            routes = [str(route.path) for route in app.routes]
            expected_routes = ["/", "/health"]

            all_routes_found = True
            for route in expected_routes:
                if route in routes:
                    self.log_result(f"Web Server: Route {route}", True, "Route configured")
                else:
                    self.log_result(f"Web Server: Route {route}", False, "Route missing")
                    all_routes_found = False

            return all_routes_found

        except Exception as e:
            self.log_result("Web Server", False, f"Configuration error: {e}")
            return False

    def test_cli_interface(self) -> bool:
        """Test CLI interface."""
        try:
            from cli import main

            # Test help output
            main(["--help"])
            # CLI help exits with code 0, but we catch any import/syntax errors
            self.log_result("CLI: Interface", True, "CLI module loaded successfully")

            return True

        except SystemExit:
            # Expected for --help
            self.log_result("CLI: Interface", True, "CLI help command works")
            return True
        except Exception as e:
            self.log_result("CLI: Interface", False, f"CLI error: {e}")
            return False

    def test_demo_scripts(self) -> bool:
        """Test that demo scripts can be imported."""
        demo_scripts = ["demo_calculator.py", "demo_file_server.py", "demo_all_servers.py"]

        all_success = True

        for script in demo_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                self.log_result(f"Demo: {script}", True, "Script exists")
            else:
                self.log_result(f"Demo: {script}", False, "Script missing")
                all_success = False

        return all_success

    def test_configuration_files(self) -> bool:
        """Test that configuration files exist."""
        config_files = {
            "requirements.txt": "Python dependencies",
            "environment.yml": "Conda environment",
            "pyproject.toml": "Project configuration",
            "README.md": "Documentation",
            "LICENSE": "License file",
        }

        for file_name, description in config_files.items():
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log_result(f"Config: {file_name}", True, description)
            else:
                self.log_result(f"Config: {file_name}", False, f"Missing {description}")
                # Don't fail for missing config files, just warn

        # Check for .env.example (optional)
        env_example = self.project_root / ".env.example"
        if env_example.exists():
            self.log_result("Config: .env.example", True, "Environment template")
        else:
            self.log_result("Config: .env.example", False, "Missing environment template (optional)")

        return True  # Config files are not critical for basic functionality

    def run_performance_test(self) -> bool:
        """Run a quick performance test."""
        try:
            import time

            from mcp_servers.calculator_server import CalculatorServer

            calc = CalculatorServer()

            # Time 100 calculations
            start_time = time.time()
            for i in range(100):
                calc.add(i, i + 1)
            end_time = time.time()

            duration = end_time - start_time
            ops_per_second = 100 / duration

            if ops_per_second > 1000:  # Should be much faster than this
                self.log_result("Performance: Calculator", True, f"{ops_per_second:.0f} ops/second")
                return True
            else:
                self.log_result("Performance: Calculator", False, f"Only {ops_per_second:.0f} ops/second (slow)")
                return False

        except Exception as e:
            self.log_result("Performance: Calculator", False, f"Error: {e}")
            return False

    def generate_summary(self) -> dict[str, Any]:
        """Generate a summary of all test results."""
        total_tests = len(self.results)
        passed_tests = sum(1 for _, success, _ in self.results if success)
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": success_rate,
            "overall_success": failed_tests == 0,
        }

    def run_all_tests(self) -> bool:
        """Run all verification tests."""
        print("🚀 MCP Demo Setup Verification")
        print("=" * 60)
        print("Running comprehensive setup verification...")
        print()

        # Run all tests
        test_methods = [
            self.test_python_version,
            self.test_dependencies,
            self.test_project_structure,
            self.test_core_imports,
            self.test_calculator_server,
            self.test_file_server,
            self.test_web_server_config,
            self.test_cli_interface,
            self.test_demo_scripts,
            self.test_configuration_files,
            self.run_performance_test,
        ]

        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_result(test_method.__name__, False, f"Test execution error: {e}")
            print()  # Add spacing between test groups

        # Generate and display summary
        summary = self.generate_summary()

        print("=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print()

        if summary["overall_success"]:
            print("🎉 ALL TESTS PASSED!")
            print("MCP Demo is ready to use!")
            print()
            print("🚀 Quick Start:")
            print("1. Try the demos:")
            print("   • python demo_calculator.py")
            print("   • python demo_file_server.py")
            print("   • python demo_all_servers.py")
            print("2. Start the web server:")
            print("   • python cli.py server")
            print("3. Open http://localhost:8000 in your browser")
            print("4. Follow the interactive tutorials!")
        else:
            print("⚠️  Some tests failed. Please check the issues above.")
            print()
            print("🔧 Common fixes:")
            print("1. Install missing dependencies:")
            print("   • pip install -r requirements.txt")
            print("   • conda env update -f environment.yml")
            print("2. Check Python version (requires 3.8+)")
            print("3. Verify you're in the correct directory")
            print("4. Check file permissions")

        print()
        return summary["overall_success"]


def main():
    """Run the setup verification."""
    verifier = SetupVerifier()
    success = verifier.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
