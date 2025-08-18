"""Tests for the file system MCP server."""

import pathlib
import tempfile
from collections.abc import Generator

import pytest

from mcp_servers.file_server import FileSystemServer


@pytest.fixture
def temp_dir() -> Generator[pathlib.Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield pathlib.Path(temp_dir)


@pytest.fixture
def server(temp_dir: pathlib.Path) -> FileSystemServer:
    """Create a file system server with a temporary base directory."""
    return FileSystemServer(base_dir=str(temp_dir))


def test_read_file(server: FileSystemServer, temp_dir: pathlib.Path) -> None:
    """Test reading a file."""
    # Create a test file
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello, world!")

    # Read the file
    content = server.read_file("test.txt")
    assert content == "Hello, world!"


def test_read_file_not_found(server: FileSystemServer) -> None:
    """Test reading a non-existent file."""
    with pytest.raises(FileNotFoundError):
        server.read_file("non_existent.txt")


def test_read_file_outside_base_dir(server: FileSystemServer) -> None:
    """Test reading a file outside the base directory."""
    with pytest.raises(ValueError):
        server.read_file("../outside.txt")


def test_write_file(server: FileSystemServer, temp_dir: pathlib.Path) -> None:
    """Test writing to a file."""
    # Write to a file
    result = server.write_file("test.txt", "Hello, world!")
    assert result is True

    # Check that the file was created
    test_file = temp_dir / "test.txt"
    assert test_file.exists()
    assert test_file.read_text() == "Hello, world!"


def test_write_file_create_directories(server: FileSystemServer, temp_dir: pathlib.Path) -> None:
    """Test writing to a file in a non-existent directory."""
    # Write to a file in a non-existent directory
    result = server.write_file("subdir/test.txt", "Hello, world!")
    assert result is True

    # Check that the file was created
    test_file = temp_dir / "subdir" / "test.txt"
    assert test_file.exists()
    assert test_file.read_text() == "Hello, world!"


def test_write_file_outside_base_dir(server: FileSystemServer) -> None:
    """Test writing to a file outside the base directory."""
    with pytest.raises(ValueError):
        server.write_file("../outside.txt", "Hello, world!")


def test_list_directory(server: FileSystemServer, temp_dir: pathlib.Path) -> None:
    """Test listing a directory."""
    # Create some test files
    (temp_dir / "file1.txt").write_text("File 1")
    (temp_dir / "file2.txt").write_text("File 2")
    (temp_dir / "subdir").mkdir()
    (temp_dir / "subdir" / "file3.txt").write_text("File 3")

    # List the directory
    files = server.list_directory(".")

    # Check that the files were listed
    assert len(files) == 3
    assert any(f["path"] == "file1.txt" for f in files)
    assert any(f["path"] == "file2.txt" for f in files)
    assert any(f["path"] == "subdir" for f in files)

    # Check file types
    for f in files:
        if f["path"] == "subdir":
            assert f["type"] == "directory"
        else:
            assert f["type"] == "file"


def test_list_directory_recursive(server: FileSystemServer, temp_dir: pathlib.Path) -> None:
    """Test listing a directory recursively."""
    # Create some test files
    (temp_dir / "file1.txt").write_text("File 1")
    (temp_dir / "subdir").mkdir()
    (temp_dir / "subdir" / "file2.txt").write_text("File 2")

    # List the directory recursively
    files = server.list_directory(".", recursive=True)

    # Check that the files were listed
    assert len(files) == 3
    assert any(f["path"] == "file1.txt" for f in files)
    assert any(f["path"] == "subdir" for f in files)
    assert any(f["path"] == "subdir/file2.txt" for f in files)


def test_list_directory_not_found(server: FileSystemServer) -> None:
    """Test listing a non-existent directory."""
    with pytest.raises(FileNotFoundError):
        server.list_directory("non_existent")


def test_list_directory_not_a_directory(server: FileSystemServer, temp_dir: pathlib.Path) -> None:
    """Test listing a file as a directory."""
    # Create a test file
    (temp_dir / "test.txt").write_text("Hello, world!")

    with pytest.raises(ValueError):
        server.list_directory("test.txt")


def test_path_exists(server: FileSystemServer, temp_dir: pathlib.Path) -> None:
    """Test checking if a path exists."""
    # Create a test file and directory
    (temp_dir / "test.txt").write_text("Hello, world!")
    (temp_dir / "subdir").mkdir()

    # Check if paths exist
    assert server.path_exists("test.txt") is True
    assert server.path_exists("subdir") is True
    assert server.path_exists("non_existent.txt") is False


def test_path_exists_outside_base_dir(server: FileSystemServer) -> None:
    """Test checking if a path outside the base directory exists."""
    assert server.path_exists("../outside.txt") is False


def test_file_info(server: FileSystemServer, temp_dir: pathlib.Path) -> None:
    """Test getting file information."""
    # Create a test file
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello, world!")

    # Get file information
    info = server.file_info("test.txt")

    # Check the information
    assert info["path"] == "test.txt"
    assert info["type"] == "file"
    assert info["size"] == 13  # Length of "Hello, world!"
    assert "created" in info
    assert "modified" in info
    assert "accessed" in info


def test_file_info_directory(server: FileSystemServer, temp_dir: pathlib.Path) -> None:
    """Test getting information about a directory."""
    # Create a test directory
    (temp_dir / "subdir").mkdir()

    # Get directory information
    info = server.file_info("subdir")

    # Check the information
    assert info["path"] == "subdir"
    assert info["type"] == "directory"


def test_file_info_not_found(server: FileSystemServer) -> None:
    """Test getting information about a non-existent file."""
    with pytest.raises(FileNotFoundError):
        server.file_info("non_existent.txt")


def test_file_info_outside_base_dir(server: FileSystemServer) -> None:
    """Test getting information about a file outside the base directory."""
    with pytest.raises(ValueError):
        server.file_info("../outside.txt")
