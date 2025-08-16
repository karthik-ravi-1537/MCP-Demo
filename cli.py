"""Command line interface for MCP Demo Project."""

import argparse
import sys
from typing import List, Optional


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the MCP Demo Project CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code
    """
    if args is None:
        args = sys.argv[1:]
        
    parser = argparse.ArgumentParser(
        description="MCP Demo Project - Learn Model Context Protocol from beginner to expert"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run the web server")
    server_parser.add_argument(
        "--host", 
        default="localhost", 
        help="Host to bind to (default: localhost)"
    )
    server_parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind to (default: 8000)"
    )
    server_parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    if parsed_args.command == "server":
        return run_server(
            host=parsed_args.host,
            port=parsed_args.port,
            reload=parsed_args.reload
        )
    
    return 0


def run_server(host: str, port: int, reload: bool) -> int:
    """Run the web server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Whether to enable auto-reload
        
    Returns:
        Exit code
    """
    try:
        import uvicorn
        
        print(f"Starting server on {host}:{port}")
        uvicorn.run(
            "server:app",
            host=host,
            port=port,
            reload=reload
        )
        return 0
    except ImportError:
        print("Error: uvicorn not installed. Please install with 'pip install uvicorn[standard]'")
        return 1
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())