"""Tests for the calculator MCP server."""

import math
import pytest

from mcp_servers.calculator_server import CalculatorServer


@pytest.fixture
def server():
    """Create a calculator server."""
    return CalculatorServer()


def test_add(server):
    """Test the add tool."""
    assert server.add(1, 2) == 3
    assert server.add(1.5, 2.5) == 4.0
    assert server.add(-1, 1) == 0
    assert server.add(0, 0) == 0


def test_subtract(server):
    """Test the subtract tool."""
    assert server.subtract(5, 3) == 2
    assert server.subtract(3, 5) == -2
    assert server.subtract(1.5, 0.5) == 1.0
    assert server.subtract(0, 0) == 0


def test_multiply(server):
    """Test the multiply tool."""
    assert server.multiply(2, 3) == 6
    assert server.multiply(2.5, 2) == 5.0
    assert server.multiply(-2, 3) == -6
    assert server.multiply(0, 5) == 0


def test_divide(server):
    """Test the divide tool."""
    assert server.divide(6, 2) == 3.0
    assert server.divide(5, 2) == 2.5
    assert server.divide(-6, 2) == -3.0
    assert server.divide(0, 5) == 0.0
    
    # Test division by zero
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        server.divide(5, 0)


def test_power(server):
    """Test the power tool."""
    assert server.power(2, 3) == 8.0
    assert server.power(2, 0) == 1.0
    assert server.power(0, 5) == 0.0
    assert server.power(2, -1) == 0.5


def test_sqrt(server):
    """Test the sqrt tool."""
    assert server.sqrt(9) == 3.0
    assert server.sqrt(2) == pytest.approx(1.4142, 0.0001)
    assert server.sqrt(0) == 0.0
    
    # Test square root of a negative number
    with pytest.raises(ValueError, match="Cannot calculate square root of a negative number"):
        server.sqrt(-1)


def test_abs(server):
    """Test the abs tool."""
    assert server.abs(5) == 5
    assert server.abs(-5) == 5
    assert server.abs(0) == 0
    assert server.abs(-3.14) == 3.14


def test_round(server):
    """Test the round tool."""
    assert server.round(3.14159) == 3
    assert server.round(3.14159, 2) == 3.14
    assert server.round(3.5) == 4
    assert server.round(-3.5) == -4
    assert server.round(0) == 0


def test_factorial(server):
    """Test the factorial tool."""
    assert server.factorial(0) == 1
    assert server.factorial(1) == 1
    assert server.factorial(5) == 120
    
    # Test factorial of a negative number
    with pytest.raises(ValueError, match="Cannot calculate factorial of a negative number"):
        server.factorial(-1)


def test_gcd(server):
    """Test the gcd tool."""
    assert server.gcd(12, 8) == 4
    assert server.gcd(17, 13) == 1
    assert server.gcd(0, 5) == 5
    assert server.gcd(0, 0) == 0


def test_get_tutorial_content(server):
    """Test getting tutorial content."""
    content = server.get_tutorial_content()
    assert "Calculator MCP Server" in content
    assert "add" in content
    assert "subtract" in content
    assert "multiply" in content
    assert "divide" in content


def test_get_example_code(server):
    """Test getting example code."""
    examples = server.get_example_code()
    assert "basic_operations" in examples
    assert "advanced_operations" in examples
    assert "calculator_app" in examples