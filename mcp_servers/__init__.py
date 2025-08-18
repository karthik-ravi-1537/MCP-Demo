"""MCP server implementations for the demo project."""

from .base import BaseMCPServer
from .calculator_server import CalculatorServer

# Import server implementations
from .file_server import FileSystemServer

# These will be uncommented as we implement each server
# from .text_server import TextProcessingServer
# from .system_server import SystemInfoServer
# from .web_server import WebAPIServer
# from .db_server import DatabaseServer
# from .weather_server import WeatherServer
# from .advanced_server import AdvancedServer


# Server registry
SERVER_TYPES: dict[str, type[BaseMCPServer]] = {
    "file": FileSystemServer,
    "calc": CalculatorServer,
    # "text": TextProcessingServer,
    # "system": SystemInfoServer,
    # "web": WebAPIServer,
    # "db": DatabaseServer,
    # "weather": WeatherServer,
    # "advanced": AdvancedServer,
}


def create_server(server_type: str) -> BaseMCPServer:
    """Create an MCP server of the specified type."""
    if server_type not in SERVER_TYPES:
        raise ValueError(f"Unknown server type: {server_type}")

    server_class = SERVER_TYPES[server_type]
    return server_class()
