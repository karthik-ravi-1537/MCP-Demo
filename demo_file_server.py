#!/usr/bin/env python3
"""
Demo script for MCP File System Server
======================================

This demo shows how to use the File System MCP server for file operations.
Demonstrates secure file handling and MCP tool patterns.

Run with: python demo_file_server.py
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp_servers.file_server import FileSystemServer


async def demo_basic_file_operations():
    """Demonstrate basic file operations."""
    print("📁 Basic File Operations")
    print("=" * 50)
    
    # Create a temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Working in temporary directory: {temp_dir}")
        
        # Initialize file server with the temp directory as base
        file_server = FileSystemServer(base_dir=temp_dir)
        
        # Demo file content
        demo_content = """# MCP Demo File
This is a demonstration file created by the MCP File System Server.

## Features
- Secure file operations
- Directory traversal protection
- Multiple file format support

Created by: MCP Demo
Date: Today
"""
        
        # Test file operations
        demo_file = "demo.md"
        
        try:
            # Write file
            print(f"✅ Writing file: {demo_file}")
            file_server.write_file(demo_file, demo_content)
            
            # Read file
            print(f"✅ Reading file: {demo_file}")
            content = file_server.read_file(demo_file)
            print(f"   Content preview: {content[:50]}...")
            
            # List directory
            print("✅ Listing directory contents:")
            files = file_server.list_directory(".")
            for file_info in files:
                print(f"   • {file_info['name']} ({file_info['type']})")
            
            # Get file info
            print(f"✅ Getting file info for: {demo_file}")
            file_info = file_server.get_file_info(demo_file)
            print(f"   Size: {file_info['size']} bytes")
            print(f"   Type: {file_info['type']}")
            
            # Delete file
            print(f"✅ Deleting file: {demo_file}")
            file_server.delete_file(demo_file)
            
            # Verify deletion
            files_after = file_server.list_directory(".")
            print(f"✅ Files after deletion: {len(files_after)}")
            
        except Exception as e:
            print(f"❌ File operation failed: {e}")
    
    print()


async def demo_directory_operations():
    """Demonstrate directory operations."""
    print("📂 Directory Operations")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_server = FileSystemServer(base_dir=temp_dir)
        
        try:
            # Create directories
            directories = ["projects", "projects/mcp-demo", "documents", "temp"]
            
            for dir_name in directories:
                print(f"✅ Creating directory: {dir_name}")
                file_server.create_directory(dir_name)
            
            # Create files in different directories
            files = {
                "projects/mcp-demo/README.md": "# MCP Demo Project\\nThis is the main project file.",
                "projects/mcp-demo/config.json": '{"name": "mcp-demo", "version": "1.0.0"}',
                "documents/notes.txt": "Important notes for the project",
                "temp/temporary.log": "Temporary log file content"
            }
            
            for file_path, content in files.items():
                print(f"✅ Creating file: {file_path}")
                file_server.write_file(file_path, content)
            
            # List directory tree
            print("✅ Directory tree:")
            def show_directory_tree(path, prefix=""):
                try:
                    items = file_server.list_directory(path)
                    for item in sorted(items, key=lambda x: (x['type'], x['name'])):
                        print(f"{prefix}{'📁' if item['type'] == 'directory' else '📄'} {item['name']}")
                        if item['type'] == 'directory':
                            sub_path = os.path.join(path, item['name']).replace("\\\\", "/")
                            show_directory_tree(sub_path, prefix + "  ")
                except Exception as e:
                    print(f"{prefix}❌ Error listing {path}: {e}")
            
            show_directory_tree(".")
            
            # Search for files
            print("✅ Searching for .md files:")
            md_files = file_server.search_files(pattern="*.md")
            for file_path in md_files:
                print(f"   • {file_path}")
            
        except Exception as e:
            print(f"❌ Directory operation failed: {e}")
    
    print()


async def demo_file_content_operations():
    """Demonstrate file content operations."""
    print("📝 File Content Operations")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_server = FileSystemServer(base_dir=temp_dir)
        
        # Create a sample text file
        sample_content = """Line 1: Introduction to MCP
Line 2: Model Context Protocol
Line 3: Enables AI tool usage
Line 4: Secure and standardized
Line 5: Built for the future"""
        
        try:
            # Write initial content
            file_server.write_file("sample.txt", sample_content)
            
            # Append content
            print("✅ Appending content to file")
            additional_content = "\\nLine 6: Added via append operation"
            file_server.append_to_file("sample.txt", additional_content)
            
            # Read specific lines
            print("✅ Reading specific lines:")
            full_content = file_server.read_file("sample.txt")
            lines = full_content.split("\\n")
            for i, line in enumerate(lines[:3], 1):
                print(f"   Line {i}: {line}")
            
            # Copy file
            print("✅ Copying file")
            file_server.copy_file("sample.txt", "sample_copy.txt")
            
            # Move file
            print("✅ Moving file")
            file_server.move_file("sample_copy.txt", "moved_sample.txt")
            
            # Verify operations
            files = file_server.list_directory(".")
            print(f"✅ Final file count: {len(files)}")
            for file_info in files:
                print(f"   • {file_info['name']}")
            
        except Exception as e:
            print(f"❌ Content operation failed: {e}")
    
    print()


async def demo_security_features():
    """Demonstrate security features and error handling."""
    print("🔒 Security and Error Handling")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_server = FileSystemServer(base_dir=temp_dir)
        
        # Test various security scenarios
        security_tests = [
            ("../../../etc/passwd", "Path traversal attempt"),
            ("..\\\\..\\\\..\\\\windows\\\\system32", "Windows path traversal"),
            ("/etc/passwd", "Absolute path access"),
            ("", "Empty filename"),
            ("con.txt", "Reserved filename (Windows)"),
        ]
        
        for test_path, description in security_tests:
            try:
                file_server.read_file(test_path)
                print(f"❌ {description}: Should have been blocked")
            except Exception as e:
                print(f"✅ {description}: Correctly blocked - {type(e).__name__}")
        
        # Test error handling for missing files
        try:
            file_server.read_file("nonexistent.txt")
            print("❌ Reading nonexistent file: Should have failed")
        except Exception as e:
            print(f"✅ Nonexistent file: Correctly handled - {type(e).__name__}")
        
        # Test error handling for directory operations
        try:
            file_server.create_directory("test")
            file_server.create_directory("test")  # Try to create again
            print("❌ Duplicate directory: Should have handled gracefully")
        except Exception as e:
            print(f"✅ Duplicate directory: Handled - {type(e).__name__}")
    
    print()


async def demo_server_info():
    """Display server information and available tools."""
    print("📋 File Server Information")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_server = FileSystemServer(base_dir=temp_dir)
        
        print(f"Server Name: {file_server.name}")
        print(f"Description: {file_server.description}")
        print(f"Root Directory: {temp_dir}")
        print(f"Available Tools: {len(file_server.tools)}")
        print()
        
        print("Available Tools:")
        for tool_name in file_server.tools.keys():
            tool_def = file_server.tool_definitions.get(tool_name)
            description = tool_def.description if tool_def else "No description"
            print(f"  • {tool_name}: {description}")
    
    print()


async def interactive_file_explorer():
    """Run an interactive file explorer session."""
    print("🎮 Interactive File Explorer")
    print("=" * 50)
    print("Commands: ls, read <file>, write <file> <content>, mkdir <dir>, help, quit")
    print()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_server = FileSystemServer(base_dir=temp_dir)
        current_dir = "."
        
        print(f"Working directory: {temp_dir}")
        print()
        
        while True:
            try:
                user_input = input(f"file_explorer:{current_dir}> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    print("Available commands:")
                    print("  ls [dir]           - List directory contents")
                    print("  read <file>        - Read file content")
                    print("  write <file> <content> - Write content to file")
                    print("  mkdir <dir>        - Create directory")
                    print("  rm <file>          - Delete file")
                    print("  info <file>        - Get file information")
                    print("  help               - Show this help")
                    print("  quit               - Exit")
                    continue
                
                parts = user_input.split(maxsplit=2)
                if len(parts) == 0:
                    continue
                
                command = parts[0].lower()
                
                try:
                    if command == 'ls':
                        target_dir = parts[1] if len(parts) > 1 else current_dir
                        files = file_server.list_directory(target_dir)
                        if not files:
                            print("Directory is empty")
                        else:
                            for file_info in files:
                                icon = "📁" if file_info['type'] == 'directory' else "📄"
                                print(f"  {icon} {file_info['name']}")
                    
                    elif command == 'read':
                        if len(parts) < 2:
                            print("❌ Please specify a file to read")
                            continue
                        content = file_server.read_file(parts[1])
                        print("File content:")
                        print(content)
                    
                    elif command == 'write':
                        if len(parts) < 3:
                            print("❌ Please specify file and content")
                            continue
                        file_server.write_file(parts[1], parts[2])
                        print(f"✅ Written to {parts[1]}")
                    
                    elif command == 'mkdir':
                        if len(parts) < 2:
                            print("❌ Please specify directory name")
                            continue
                        file_server.create_directory(parts[1])
                        print(f"✅ Created directory {parts[1]}")
                    
                    elif command == 'rm':
                        if len(parts) < 2:
                            print("❌ Please specify file to delete")
                            continue
                        file_server.delete_file(parts[1])
                        print(f"✅ Deleted {parts[1]}")
                    
                    elif command == 'info':
                        if len(parts) < 2:
                            print("❌ Please specify file")
                            continue
                        info = file_server.get_file_info(parts[1])
                        print(f"File: {parts[1]}")
                        print(f"  Type: {info['type']}")
                        print(f"  Size: {info['size']} bytes")
                        if 'modified' in info:
                            print(f"  Modified: {info['modified']}")
                    
                    else:
                        print(f"❌ Unknown command: {command}")
                        print("Type 'help' for available commands")
                
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except EOFError:
                print("\\n👋 Goodbye!")
                break


async def main():
    """Run the complete file server demo."""
    print("🚀 MCP File System Server Demo")
    print("=" * 70)
    print("This demo showcases the Model Context Protocol (MCP) File System Server")
    print("Learn secure file operations and MCP tool patterns!")
    print("=" * 70)
    print()
    
    # Run all demo sections
    await demo_server_info()
    await demo_basic_file_operations()
    await demo_directory_operations()
    await demo_file_content_operations()
    await demo_security_features()
    
    # Ask if user wants interactive mode
    try:
        response = input("Would you like to try the interactive file explorer? (y/N): ")
        if response.lower().startswith('y'):
            await interactive_file_explorer()
    except (KeyboardInterrupt, EOFError):
        pass
    
    print("\\n🎉 Demo completed successfully!")
    print("\\nNext steps:")
    print("1. Explore the file server code in mcp_servers/file_server.py")
    print("2. Try the calculator demo: python demo_calculator.py")
    print("3. Start the web server: python cli.py server")
    print("4. Visit http://localhost:8000 for interactive tutorials")


if __name__ == "__main__":
    asyncio.run(main())
