"""File system MCP server implementation."""

import os
import pathlib
from typing import Dict, List, Optional

from .base import BaseMCPServer, tool


class FileSystemServer(BaseMCPServer):
    """MCP server for file system operations."""
    
    def __init__(
        self,
        name: str = "file_system",
        description: str = "File system operations",
        base_dir: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the file system server.
        
        Args:
            name: Name of the server.
            description: Description of the server.
            base_dir: Base directory for file operations. If not provided,
                uses the current working directory.
            **kwargs: Additional arguments to pass to BaseMCPServer.
        """
        super().__init__(name=name, description=description, **kwargs)
        self.base_dir = pathlib.Path(base_dir or os.getcwd()).resolve()
        self.logger.info(f"Base directory: {self.base_dir}")
    
    def _resolve_path(self, path: str) -> pathlib.Path:
        """Resolve a path relative to the base directory.
        
        Args:
            path: Path to resolve.
            
        Returns:
            Resolved path.
            
        Raises:
            ValueError: If the path is outside the base directory.
        """
        # Resolve the path
        resolved = (self.base_dir / path).resolve()
        
        # Check that the path is within the base directory
        if not str(resolved).startswith(str(self.base_dir)):
            raise ValueError(f"Path {path} is outside the base directory")
        
        return resolved
    
    @tool(
        description="Read a file from the file system",
        category="filesystem",
        tags=["file", "read"],
    )
    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """Read a file from the file system.
        
        Args:
            path: Path to the file, relative to the base directory.
            encoding: File encoding.
            
        Returns:
            File contents.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the path is outside the base directory.
        """
        resolved_path = self._resolve_path(path)
        
        if not resolved_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not resolved_path.is_file():
            raise ValueError(f"Not a file: {path}")
        
        with open(resolved_path, "r", encoding=encoding) as f:
            return f.read()
    
    @tool(
        description="Write to a file in the file system",
        category="filesystem",
        tags=["file", "write"],
    )
    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> bool:
        """Write to a file in the file system.
        
        Args:
            path: Path to the file, relative to the base directory.
            content: Content to write.
            encoding: File encoding.
            
        Returns:
            True if successful.
            
        Raises:
            ValueError: If the path is outside the base directory.
        """
        resolved_path = self._resolve_path(path)
        
        # Create parent directories if they don't exist
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(resolved_path, "w", encoding=encoding) as f:
            f.write(content)
        
        return True
    
    @tool(
        description="List files in a directory",
        category="filesystem",
        tags=["file", "directory", "list"],
    )
    def list_directory(self, path: str = ".", recursive: bool = False) -> List[Dict[str, str]]:
        """List files in a directory.
        
        Args:
            path: Path to the directory, relative to the base directory.
            recursive: Whether to list files recursively.
            
        Returns:
            List of file information dictionaries.
            
        Raises:
            FileNotFoundError: If the directory does not exist.
            ValueError: If the path is outside the base directory or not a directory.
        """
        resolved_path = self._resolve_path(path)
        
        if not resolved_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        if not resolved_path.is_dir():
            raise ValueError(f"Not a directory: {path}")
        
        result = []
        
        if recursive:
            for item in resolved_path.glob("**/*"):
                relative = item.relative_to(self.base_dir)
                result.append({
                    "path": str(relative),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": item.stat().st_mtime,
                })
        else:
            for item in resolved_path.iterdir():
                relative = item.relative_to(self.base_dir)
                result.append({
                    "path": str(relative),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": item.stat().st_mtime,
                })
        
        return result
    
    @tool(
        description="Check if a file or directory exists",
        category="filesystem",
        tags=["file", "directory", "exists"],
    )
    def path_exists(self, path: str) -> bool:
        """Check if a file or directory exists.
        
        Args:
            path: Path to check, relative to the base directory.
            
        Returns:
            True if the path exists, False otherwise.
            
        Raises:
            ValueError: If the path is outside the base directory.
        """
        try:
            resolved_path = self._resolve_path(path)
            return resolved_path.exists()
        except ValueError:
            # Path is outside the base directory
            return False
    
    @tool(
        description="Get file information",
        category="filesystem",
        tags=["file", "info"],
    )
    def file_info(self, path: str) -> Dict[str, str]:
        """Get information about a file.
        
        Args:
            path: Path to the file, relative to the base directory.
            
        Returns:
            File information.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the path is outside the base directory.
        """
        resolved_path = self._resolve_path(path)
        
        if not resolved_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        stat = resolved_path.stat()
        
        return {
            "path": str(resolved_path.relative_to(self.base_dir)),
            "type": "directory" if resolved_path.is_dir() else "file",
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "accessed": stat.st_atime,
        }
    
    def get_tutorial_content(self) -> str:
        """Get tutorial content for this server."""
        return """# File System MCP Server

This server provides tools for interacting with the file system.

## Tools

### read_file

Read a file from the file system.

```python
result = await client.call_tool("read_file", {
    "path": "example.txt",
    "encoding": "utf-8"
})
print(result)  # File contents
```

### write_file

Write to a file in the file system.

```python
success = await client.call_tool("write_file", {
    "path": "example.txt",
    "content": "Hello, world!",
    "encoding": "utf-8"
})
print(success)  # True if successful
```

### list_directory

List files in a directory.

```python
files = await client.call_tool("list_directory", {
    "path": ".",
    "recursive": False
})
for file in files:
    print(f"{file['path']} - {file['type']} - {file['size']} bytes")
```

### path_exists

Check if a file or directory exists.

```python
exists = await client.call_tool("path_exists", {
    "path": "example.txt"
})
print(exists)  # True if the file exists
```

### file_info

Get information about a file.

```python
info = await client.call_tool("file_info", {
    "path": "example.txt"
})
print(f"Size: {info['size']} bytes")
print(f"Modified: {info['modified']}")
```

## Security Considerations

- The server restricts file operations to a base directory.
- Attempts to access files outside the base directory will result in an error.
- The server does not provide tools for deleting files or executing commands.
"""
    
    def get_example_code(self) -> Dict[str, str]:
        """Get example code for this server."""
        return {
            "read_file": """
import asyncio
from mcp_client import MCPClient

async def main():
    client = MCPClient("ws://localhost:5000")
    await client.connect()
    
    # Read a file
    content = await client.call_tool("read_file", {
        "path": "example.txt"
    })
    print(content)
    
    await client.disconnect()

asyncio.run(main())
""",
            "write_file": """
import asyncio
from mcp_client import MCPClient

async def main():
    client = MCPClient("ws://localhost:5000")
    await client.connect()
    
    # Write to a file
    success = await client.call_tool("write_file", {
        "path": "example.txt",
        "content": "Hello, world!"
    })
    print(f"Write successful: {success}")
    
    await client.disconnect()

asyncio.run(main())
""",
            "list_directory": """
import asyncio
from mcp_client import MCPClient

async def main():
    client = MCPClient("ws://localhost:5000")
    await client.connect()
    
    # List files in the current directory
    files = await client.call_tool("list_directory", {
        "path": ".",
        "recursive": False
    })
    
    for file in files:
        print(f"{file['path']} - {file['type']} - {file['size']} bytes")
    
    await client.disconnect()

asyncio.run(main())
""",
        }