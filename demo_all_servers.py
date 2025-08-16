#!/usr/bin/env python3
"""
Comprehensive MCP Demo - All Servers
====================================

This demo showcases all MCP servers in the project:
- Calculator Server: Mathematical operations
- File System Server: Secure file operations
- Tutorial progression and learning paths

Perfect for understanding the full MCP ecosystem!

Run with: python demo_all_servers.py
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp_servers.calculator_server import CalculatorServer
from mcp_servers.file_server import FileSystemServer


async def demo_mcp_overview():
    """Provide an overview of MCP and available servers."""
    print("🌟 Model Context Protocol (MCP) Demo")
    print("=" * 70)
    print("""
The Model Context Protocol (MCP) enables AI agents to securely interact with
tools and services. This demo showcases multiple MCP servers working together
to provide a comprehensive tool ecosystem.

🧮 Calculator Server: Mathematical operations and calculations
📁 File System Server: Secure file and directory operations
🌐 Web Interface: Interactive tutorials and documentation
    """)
    print("=" * 70)
    print()


async def demo_calculator_integration():
    """Demonstrate calculator operations in context."""
    print("🧮 Calculator Server Integration")
    print("=" * 50)
    
    calc = CalculatorServer()
    
    # Simulate a practical calculation scenario
    print("Scenario: Calculating project metrics")
    print()
    
    # Project statistics
    lines_of_code = 1250
    files_count = 15
    average_lines_per_file = calc.divide(lines_of_code, files_count)
    
    # Calculate project complexity score
    complexity_base = calc.multiply(average_lines_per_file, 0.8)
    complexity_factor = calc.power(files_count, 0.3)
    complexity_score = calc.multiply(complexity_base, complexity_factor)
    rounded_score = calc.round(complexity_score, 2)
    
    print(f"✅ Total lines of code: {lines_of_code}")
    print(f"✅ Number of files: {files_count}")
    print(f"✅ Average lines per file: {average_lines_per_file}")
    print(f"✅ Project complexity score: {rounded_score}")
    
    # Statistical calculations
    print("\\nStatistical analysis:")
    test_scores = [85, 92, 78, 96, 88, 91, 87, 94]
    
    # Calculate mean (using add and divide)
    total = 0
    for score in test_scores:
        total = calc.add(total, score)
    mean_score = calc.divide(total, len(test_scores))
    
    # Find max and min using comparisons
    max_score = max(test_scores)
    min_score = min(test_scores)
    range_score = calc.subtract(max_score, min_score)
    
    print(f"✅ Test scores: {test_scores}")
    print(f"✅ Mean score: {calc.round(mean_score, 2)}")
    print(f"✅ Score range: {range_score} (max: {max_score}, min: {min_score})")
    
    print()


async def demo_file_system_integration():
    """Demonstrate file system operations in context."""
    print("📁 File System Server Integration")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_server = FileSystemServer(base_dir=temp_dir)
        
        print("Scenario: Setting up a project workspace")
        print()
        
        # Create project structure
        project_structure = {
            "src": "directory",
            "tests": "directory", 
            "docs": "directory",
            "config": "directory"
        }
        
        for name, item_type in project_structure.items():
            if item_type == "directory":
                file_server.create_directory(name)
                print(f"✅ Created directory: {name}/")
        
        # Create project files
        project_files = {
            "README.md": """# MCP Demo Project
            
This project demonstrates the Model Context Protocol (MCP) with multiple servers.

## Features
- Calculator operations
- File system management
- Interactive tutorials

## Getting Started
Run the demos to explore MCP capabilities!
""",
            "src/main.py": """#!/usr/bin/env python3
# Main application entry point
from mcp_servers import CalculatorServer, FileSystemServer

def main():
    print("MCP Demo Application")
    # Application logic here
    
if __name__ == "__main__":
    main()
""",
            "tests/test_calculator.py": """import pytest
from mcp_servers.calculator_server import CalculatorServer

def test_basic_operations():
    calc = CalculatorServer()
    assert calc.add(2, 3) == 5
    assert calc.multiply(4, 5) == 20
""",
            "config/settings.json": """{
    "server_port": 8000,
    "debug": true,
    "calculator_enabled": true,
    "file_server_enabled": true
}""",
            "docs/api.md": """# API Documentation

## Calculator Server
- add(a, b): Addition
- multiply(a, b): Multiplication
- divide(a, b): Division

## File Server
- read_file(path): Read file content
- write_file(path, content): Write to file
"""
        }
        
        for file_path, content in project_files.items():
            file_server.write_file(file_path, content)
            print(f"✅ Created file: {file_path}")
        
        # Demonstrate file operations
        print("\\nProject analysis:")
        
        # Count files in each directory
        for directory in ["src", "tests", "docs", "config"]:
            try:
                files = file_server.list_directory(directory)
                file_count = len([f for f in files if f['type'] == 'file'])
                print(f"✅ {directory}/: {file_count} files")
            except Exception as e:
                print(f"❌ Error analyzing {directory}/: {e}")
        
        # Get project statistics
        all_files = file_server.search_files("*")
        total_size = 0
        for file_path in all_files:
            try:
                info = file_server.get_file_info(file_path)
                total_size += info['size']
            except:
                pass
        
        print(f"✅ Total project files: {len(all_files)}")
        print(f"✅ Total project size: {total_size} bytes")
        
    print()


async def demo_integrated_workflow():
    """Demonstrate servers working together in a workflow."""
    print("🔄 Integrated Workflow Example")
    print("=" * 50)
    
    print("Scenario: Data processing pipeline")
    print()
    
    calc = CalculatorServer()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_server = FileSystemServer(base_dir=temp_dir)
        
        # Step 1: Create input data file
        input_data = """25,30,22,28,35,31,27,33,29,26
18,24,20,22,28,25,21,27,23,19
32,38,35,41,29,36,33,39,37,34"""
        
        file_server.write_file("input_data.csv", input_data)
        print("✅ Step 1: Created input data file")
        
        # Step 2: Process data using calculator
        print("✅ Step 2: Processing data...")
        
        # Read and parse data
        data_content = file_server.read_file("input_data.csv")
        rows = data_content.strip().split("\\n")
        
        results = []
        for i, row in enumerate(rows, 1):
            values = [float(x) for x in row.split(",")]
            
            # Calculate statistics using calculator server
            total = 0
            for value in values:
                total = calc.add(total, value)
            
            mean = calc.divide(total, len(values))
            max_val = max(values)
            min_val = min(values)
            range_val = calc.subtract(max_val, min_val)
            
            result_line = f"Row {i}: Mean={calc.round(mean, 2)}, Range={range_val}, Count={len(values)}"
            results.append(result_line)
            print(f"   {result_line}")
        
        # Step 3: Save processed results
        output_content = "\\n".join(results)
        file_server.write_file("processed_results.txt", output_content)
        print("✅ Step 3: Saved processed results")
        
        # Step 4: Generate summary report
        total_rows = len(rows)
        total_data_points = calc.multiply(total_rows, 10)  # 10 values per row
        
        summary = f"""# Data Processing Summary
        
Processed: {total_rows} rows
Total data points: {total_data_points}
Output files: processed_results.txt

Processing completed successfully using MCP servers:
- Calculator Server: Mathematical operations
- File System Server: Data I/O operations
"""
        
        file_server.write_file("summary_report.md", summary)
        print("✅ Step 4: Generated summary report")
        
        # Step 5: List all generated files
        print("\\n✅ Step 5: Generated files:")
        files = file_server.list_directory(".")
        for file_info in files:
            if file_info['type'] == 'file':
                size_info = file_server.get_file_info(file_info['name'])
                print(f"   📄 {file_info['name']} ({size_info['size']} bytes)")
    
    print()


async def demo_error_handling_integration():
    """Demonstrate integrated error handling across servers."""
    print("⚠️  Integrated Error Handling")
    print("=" * 50)
    
    calc = CalculatorServer()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_server = FileSystemServer(base_dir=temp_dir)
        
        print("Testing coordinated error handling:")
        
        # Test 1: Invalid calculation with file logging
        try:
            result = calc.divide(10, 0)
            print(f"❌ Division by zero should have failed, got: {result}")
        except Exception as e:
            error_log = f"Calculator Error: {type(e).__name__}: {e}\\n"
            try:
                file_server.write_file("error.log", error_log)
                print("✅ Calculator error properly caught and logged")
            except Exception as file_error:
                print(f"❌ Failed to log calculator error: {file_error}")
        
        # Test 2: File operation with calculation validation
        try:
            # Try to read non-existent config file
            config_content = file_server.read_file("nonexistent_config.json")
            print(f"❌ Should have failed to read file, got: {config_content[:20]}...")
        except Exception as e:
            print("✅ File read error properly caught")
            
            # Create default config with calculated values
            default_port = calc.add(8000, 0)  # Use calculator for consistency
            timeout_value = calc.multiply(30, 1)  # 30 seconds
            
            default_config = f"""{{"port": {default_port}, "timeout": {timeout_value}}}"""
            file_server.write_file("default_config.json", default_config)
            print("✅ Created default config using calculator values")
        
        # Test 3: Validate file content with calculations
        try:
            config_content = file_server.read_file("default_config.json")
            print(f"✅ Successfully recovered with config: {config_content}")
        except Exception as e:
            print(f"❌ Failed to read default config: {e}")
    
    print()


async def demo_performance_showcase():
    """Demonstrate performance characteristics of MCP servers."""
    print("⚡ Performance Showcase")
    print("=" * 50)
    
    import time
    
    calc = CalculatorServer()
    
    # Calculator performance test
    print("Testing calculator performance:")
    start_time = time.time()
    
    for i in range(1000):
        calc.add(i, i + 1)
        if i % 100 == 0 and i > 0:
            calc.multiply(i, 2)
    
    calc_time = time.time() - start_time
    print(f"✅ Calculator: 1000 operations in {calc_time:.4f} seconds")
    
    # File system performance test
    with tempfile.TemporaryDirectory() as temp_dir:
        file_server = FileSystemServer(base_dir=temp_dir)
        
        print("Testing file system performance:")
        start_time = time.time()
        
        # Create multiple small files
        for i in range(100):
            content = f"File {i} content with some data for testing"
            file_server.write_file(f"test_file_{i}.txt", content)
        
        # Read them back
        for i in range(100):
            try:
                content = file_server.read_file(f"test_file_{i}.txt")
            except:
                pass
        
        file_time = time.time() - start_time
        print(f"✅ File System: 200 operations in {file_time:.4f} seconds")
    
    # Combined operations
    print("Testing combined operations:")
    start_time = time.time()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_server = FileSystemServer(base_dir=temp_dir)
        
        for i in range(50):
            # Calculate value
            calculated_value = calc.multiply(i, 3)
            computed_result = calc.add(calculated_value, 10)
            
            # Store result
            result_content = f"Result for {i}: {computed_result}"
            file_server.write_file(f"result_{i}.txt", result_content)
    
    combined_time = time.time() - start_time
    print(f"✅ Combined: 150 operations in {combined_time:.4f} seconds")
    
    print()


async def main():
    """Run the comprehensive MCP demo."""
    print("🚀 Comprehensive MCP Demo - All Servers")
    print("=" * 70)
    
    await demo_mcp_overview()
    await demo_calculator_integration()
    await demo_file_system_integration()
    await demo_integrated_workflow()
    await demo_error_handling_integration()
    await demo_performance_showcase()
    
    print("🎉 Comprehensive demo completed successfully!")
    print()
    print("🎯 What you've learned:")
    print("• How MCP servers provide standardized tool interfaces")
    print("• Calculator operations for mathematical processing")
    print("• Secure file system operations with built-in protections")
    print("• Error handling patterns across different server types")
    print("• Performance characteristics of MCP server operations")
    print("• Integration patterns for building complex workflows")
    print()
    print("🚀 Next steps:")
    print("1. Try individual demos:")
    print("   • python demo_calculator.py")
    print("   • python demo_file_server.py")
    print("2. Explore server implementations in mcp_servers/")
    print("3. Start the web interface: python cli.py server")
    print("4. Visit http://localhost:8000 for interactive tutorials")
    print("5. Read the enhanced documentation in README.md")
    print()
    print("Happy learning! 🎓")


if __name__ == "__main__":
    asyncio.run(main())
