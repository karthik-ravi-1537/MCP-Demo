"""Calculator MCP server implementation."""

import math

from .base import BaseMCPServer, tool


class CalculatorServer(BaseMCPServer):
    """MCP server for calculator operations."""

    def __init__(
        self,
        name: str = "calculator",
        description: str = "Calculator operations",
        **kwargs,
    ):
        """Initialize the calculator server.

        Args:
            name: Name of the server.
            description: Description of the server.
            **kwargs: Additional arguments to pass to BaseMCPServer.
        """
        super().__init__(name=name, description=description, **kwargs)

    @tool(
        description="Add two numbers",
        category="arithmetic",
        tags=["math", "addition"],
    )
    def add(self, a: int | float, b: int | float) -> int | float:
        """Add two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Sum of the two numbers.
        """
        return a + b

    @tool(
        description="Subtract two numbers",
        category="arithmetic",
        tags=["math", "subtraction"],
    )
    def subtract(self, a: int | float, b: int | float) -> int | float:
        """Subtract two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Difference of the two numbers.
        """
        return a - b

    @tool(
        description="Multiply two numbers",
        category="arithmetic",
        tags=["math", "multiplication"],
    )
    def multiply(self, a: int | float, b: int | float) -> int | float:
        """Multiply two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Product of the two numbers.
        """
        return a * b

    @tool(
        description="Divide two numbers",
        category="arithmetic",
        tags=["math", "division"],
    )
    def divide(self, a: int | float, b: int | float) -> float:
        """Divide two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Quotient of the two numbers.

        Raises:
            ValueError: If b is zero.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")

        return a / b

    @tool(
        description="Calculate the power of a number",
        category="arithmetic",
        tags=["math", "power"],
    )
    def power(self, base: int | float, exponent: int | float) -> float:
        """Calculate the power of a number.

        Args:
            base: Base number.
            exponent: Exponent.

        Returns:
            Base raised to the power of exponent.
        """
        return math.pow(base, exponent)

    @tool(
        description="Calculate the square root of a number",
        category="arithmetic",
        tags=["math", "square root"],
    )
    def sqrt(self, x: int | float) -> float:
        """Calculate the square root of a number.

        Args:
            x: Number to calculate the square root of.

        Returns:
            Square root of x.

        Raises:
            ValueError: If x is negative.
        """
        if x < 0:
            raise ValueError("Cannot calculate square root of a negative number")

        return math.sqrt(x)

    @tool(
        description="Calculate the absolute value of a number",
        category="arithmetic",
        tags=["math", "absolute"],
    )
    def abs(self, x: int | float) -> int | float:
        """Calculate the absolute value of a number.

        Args:
            x: Number to calculate the absolute value of.

        Returns:
            Absolute value of x.
        """
        return abs(x)

    @tool(
        description="Round a number to a specified number of decimal places",
        category="arithmetic",
        tags=["math", "rounding"],
    )
    def round(self, x: float, decimals: int = 0) -> int | float:
        """Round a number to a specified number of decimal places.

        Args:
            x: Number to round.
            decimals: Number of decimal places to round to.

        Returns:
            Rounded number.
        """
        return round(x, decimals)

    @tool(
        description="Calculate the factorial of a number",
        category="arithmetic",
        tags=["math", "factorial"],
    )
    def factorial(self, n: int) -> int:
        """Calculate the factorial of a number.

        Args:
            n: Number to calculate the factorial of.

        Returns:
            Factorial of n.

        Raises:
            ValueError: If n is negative.
        """
        if n < 0:
            raise ValueError("Cannot calculate factorial of a negative number")

        return math.factorial(n)

    @tool(
        description="Calculate the greatest common divisor of two integers",
        category="arithmetic",
        tags=["math", "gcd"],
    )
    def gcd(self, a: int, b: int) -> int:
        """Calculate the greatest common divisor of two integers.

        Args:
            a: First integer.
            b: Second integer.

        Returns:
            Greatest common divisor of a and b.
        """
        return math.gcd(a, b)

    def get_tutorial_content(self) -> str:
        """Get tutorial content for this server."""
        return """# Calculator MCP Server

This server provides tools for performing calculator operations.

## Tools

### add

Add two numbers.

```python
result = await client.call_tool("add", {
    "a": 1,
    "b": 2
})
print(result)  # 3
```

### subtract

Subtract two numbers.

```python
result = await client.call_tool("subtract", {
    "a": 5,
    "b": 3
})
print(result)  # 2
```

### multiply

Multiply two numbers.

```python
result = await client.call_tool("multiply", {
    "a": 2,
    "b": 3
})
print(result)  # 6
```

### divide

Divide two numbers.

```python
result = await client.call_tool("divide", {
    "a": 6,
    "b": 2
})
print(result)  # 3.0
```

### power

Calculate the power of a number.

```python
result = await client.call_tool("power", {
    "base": 2,
    "exponent": 3
})
print(result)  # 8.0
```

### sqrt

Calculate the square root of a number.

```python
result = await client.call_tool("sqrt", {
    "x": 9
})
print(result)  # 3.0
```

### abs

Calculate the absolute value of a number.

```python
result = await client.call_tool("abs", {
    "x": -5
})
print(result)  # 5
```

### round

Round a number to a specified number of decimal places.

```python
result = await client.call_tool("round", {
    "x": 3.14159,
    "decimals": 2
})
print(result)  # 3.14
```

### factorial

Calculate the factorial of a number.

```python
result = await client.call_tool("factorial", {
    "n": 5
})
print(result)  # 120
```

### gcd

Calculate the greatest common divisor of two integers.

```python
result = await client.call_tool("gcd", {
    "a": 12,
    "b": 8
})
print(result)  # 4
```
"""

    def get_example_code(self) -> dict[str, str]:
        """Get example code for this server."""
        return {
            "basic_operations": """
import asyncio
from mcp_client import MCPClient

async def main():
    client = MCPClient("ws://localhost:5000")
    await client.connect()

    # Basic arithmetic operations
    add_result = await client.call_tool("add", {"a": 1, "b": 2})
    subtract_result = await client.call_tool("subtract", {"a": 5, "b": 3})
    multiply_result = await client.call_tool("multiply", {"a": 2, "b": 3})
    divide_result = await client.call_tool("divide", {"a": 6, "b": 2})

    print(f"Addition: {add_result}")
    print(f"Subtraction: {subtract_result}")
    print(f"Multiplication: {multiply_result}")
    print(f"Division: {divide_result}")

    await client.disconnect()

asyncio.run(main())
""",
            "advanced_operations": """
import asyncio
from mcp_client import MCPClient

async def main():
    client = MCPClient("ws://localhost:5000")
    await client.connect()

    # Advanced operations
    power_result = await client.call_tool("power", {"base": 2, "exponent": 3})
    sqrt_result = await client.call_tool("sqrt", {"x": 9})
    abs_result = await client.call_tool("abs", {"x": -5})
    round_result = await client.call_tool("round", {"x": 3.14159, "decimals": 2})
    factorial_result = await client.call_tool("factorial", {"n": 5})
    gcd_result = await client.call_tool("gcd", {"a": 12, "b": 8})

    print(f"Power: {power_result}")
    print(f"Square Root: {sqrt_result}")
    print(f"Absolute Value: {abs_result}")
    print(f"Rounded: {round_result}")
    print(f"Factorial: {factorial_result}")
    print(f"GCD: {gcd_result}")

    await client.disconnect()

asyncio.run(main())
""",
            "calculator_app": """
import asyncio
import tkinter as tk
from tkinter import messagebox
from mcp_client import MCPClient

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MCP Calculator")

        # Create input fields
        self.a_label = tk.Label(root, text="First Number:")
        self.a_label.grid(row=0, column=0, padx=5, pady=5)
        self.a_entry = tk.Entry(root)
        self.a_entry.grid(row=0, column=1, padx=5, pady=5)

        self.b_label = tk.Label(root, text="Second Number:")
        self.b_label.grid(row=1, column=0, padx=5, pady=5)
        self.b_entry = tk.Entry(root)
        self.b_entry.grid(row=1, column=1, padx=5, pady=5)

        # Create operation buttons
        self.add_button = tk.Button(root, text="Add", command=lambda: self.perform_operation("add"))
        self.add_button.grid(row=2, column=0, padx=5, pady=5)

        self.subtract_button = tk.Button(root, text="Subtract", command=lambda: self.perform_operation("subtract"))
        self.subtract_button.grid(row=2, column=1, padx=5, pady=5)

        self.multiply_button = tk.Button(root, text="Multiply", command=lambda: self.perform_operation("multiply"))
        self.multiply_button.grid(row=3, column=0, padx=5, pady=5)

        self.divide_button = tk.Button(root, text="Divide", command=lambda: self.perform_operation("divide"))
        self.divide_button.grid(row=3, column=1, padx=5, pady=5)

        # Create result label
        self.result_label = tk.Label(root, text="Result: ")
        self.result_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Initialize MCP client
        self.client = None

    async def connect_to_server(self):
        self.client = MCPClient("ws://localhost:5000")
        await self.client.connect()

    async def disconnect_from_server(self):
        if self.client:
            await self.client.disconnect()

    def perform_operation(self, operation):
        try:
            a = float(self.a_entry.get())
            b = float(self.b_entry.get())

            asyncio.create_task(self.call_operation(operation, a, b))

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    async def call_operation(self, operation, a, b):
        if not self.client:
            await self.connect_to_server()

        try:
            result = await self.client.call_tool(operation, {"a": a, "b": b})
            self.result_label.config(text=f"Result: {result}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

# Run the application
async def main():
    root = tk.Tk()
    app = CalculatorApp(root)

    try:
        await app.connect_to_server()

        while True:
            root.update()
            await asyncio.sleep(0.01)

    except tk.TclError:
        # Window was closed
        await app.disconnect_from_server()

asyncio.run(main())
""",
        }
