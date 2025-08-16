"""Tests for the CLI module."""

import pytest
from cli import main


def test_cli_help():
    """Test that the CLI shows help when no arguments are provided."""
    result = main([])
    assert result == 1  # Should exit with code 1 when showing help


def test_cli_server_command():
    """Test that the server command is recognized."""
    # This is a mock test since we can't actually start the server in a test
    with pytest.raises(SystemExit):
        main(["server", "--help"])


def test_cli_mcp_command():
    """Test that the mcp command is recognized."""
    # This is a mock test since we can't actually start an MCP server in a test
    with pytest.raises(SystemExit):
        main(["mcp", "--help"])


def test_cli_tutorial_command():
    """Test that the tutorial command is recognized."""
    # This is a mock test since we don't have actual tutorials yet
    with pytest.raises(SystemExit):
        main(["tutorial", "--help"])