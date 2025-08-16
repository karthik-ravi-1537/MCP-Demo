#!/usr/bin/env python3
"""
Demo script for MCP Calculator Server
=====================================================

This demo shows how to use the Calculator MCP server with basic operations.
Perfect for learning MCP concepts and testing the setup.

Run with: python demo_calculator.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp_servers.calculator_server import CalculatorServer


async def demo_basic_operations():
    """Demonstrate basic calculator operations."""
    print("🧮 Basic Calculator Operations")
    print("=" * 50)
    
    # Initialize the calculator server
    calc = CalculatorServer()
    
    # Basic arithmetic operations
    operations = [
        ("add", {"a": 15, "b": 25}, "Addition"),
        ("subtract", {"a": 50, "b": 20}, "Subtraction"),
        ("multiply", {"a": 7, "b": 8}, "Multiplication"),
        ("divide", {"a": 100, "b": 4}, "Division"),
        ("power", {"base": 2, "exponent": 8}, "Power"),
        ("sqrt", {"x": 64}, "Square Root"),
        ("abs", {"x": -42}, "Absolute Value"),
        ("factorial", {"n": 5}, "Factorial"),
        ("gcd", {"a": 48, "b": 18}, "Greatest Common Divisor"),
    ]
    
    for tool_name, params, description in operations:
        try:
            # Get the tool method from the calculator server
            tool_method = getattr(calc, tool_name)
            result = tool_method(**params)
            
            # Format the operation for display
            if tool_name in ["add", "subtract", "multiply", "divide"]:
                op_symbol = {
                    "add": "+", "subtract": "-", 
                    "multiply": "×", "divide": "÷"
                }[tool_name]
                print(f"✅ {description}: {params['a']} {op_symbol} {params['b']} = {result}")
            elif tool_name == "power":
                print(f"✅ {description}: {params['base']} ^ {params['exponent']} = {result}")
            elif tool_name in ["sqrt", "abs", "factorial"]:
                param_key = list(params.keys())[0]
                print(f"✅ {description}: {tool_name}({params[param_key]}) = {result}")
            elif tool_name == "gcd":
                print(f"✅ {description}: gcd({params['a']}, {params['b']}) = {result}")
            
        except Exception as e:
            print(f"❌ {description} failed: {e}")
    
    print()


async def demo_error_handling():
    """Demonstrate error handling in calculator operations."""
    print("⚠️  Error Handling Examples")
    print("=" * 50)
    
    calc = CalculatorServer()
    
    error_cases = [
        ("divide", {"a": 10, "b": 0}, "Division by zero"),
        ("sqrt", {"x": -25}, "Square root of negative number"),
        ("factorial", {"n": -5}, "Factorial of negative number"),
    ]
    
    for tool_name, params, description in error_cases:
        try:
            tool_method = getattr(calc, tool_name)
            result = tool_method(**params)
            print(f"❌ {description}: Expected error but got {result}")
        except Exception as e:
            print(f"✅ {description}: Correctly caught error - {e}")
    
    print()


async def demo_advanced_operations():
    """Demonstrate advanced calculator operations."""
    print("🎯 Advanced Operations")
    print("=" * 50)
    
    calc = CalculatorServer()
    
    # Complex calculations
    print("Calculating compound expressions:")
    
    # (15 + 25) × 2 ÷ 4
    step1 = calc.add(15, 25)  # 40
    step2 = calc.multiply(step1, 2)  # 80
    step3 = calc.divide(step2, 4)  # 20
    print(f"✅ (15 + 25) × 2 ÷ 4 = {step3}")
    
    # √(144) + 5!
    sqrt_result = calc.sqrt(144)  # 12
    factorial_result = calc.factorial(5)  # 120
    final_result = calc.add(sqrt_result, factorial_result)  # 132
    print(f"✅ √144 + 5! = {final_result}")
    
    # Power and rounding
    power_result = calc.power(2.5, 3)  # 15.625
    rounded_result = calc.round(power_result, 2)  # 15.63
    print(f"✅ 2.5³ rounded to 2 decimals = {rounded_result}")
    
    print()


async def demo_server_info():
    """Display server information and available tools."""
    print("📋 Server Information")
    print("=" * 50)
    
    calc = CalculatorServer()
    
    print(f"Server Name: {calc.name}")
    print(f"Description: {calc.description}")
    print(f"Available Tools: {len(calc.tools)}")
    print()
    
    print("Available Tools:")
    for tool_name in calc.tools.keys():
        tool_def = calc.tool_definitions.get(tool_name)
        description = tool_def.description if tool_def else "No description"
        print(f"  • {tool_name}: {description}")
    
    print()


async def interactive_calculator():
    """Run an interactive calculator session."""
    print("🎮 Interactive Calculator")
    print("=" * 50)
    print("Type operations like: add 5 3, multiply 2 4, sqrt 16")
    print("Type 'quit' to exit, 'help' for available operations")
    print()
    
    calc = CalculatorServer()
    
    while True:
        try:
            user_input = input("calculator> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("Available operations:")
                for tool_name in calc.tools.keys():
                    print(f"  • {tool_name}")
                continue
            
            # Parse simple commands
            parts = user_input.split()
            if len(parts) < 2:
                print("❌ Please provide an operation and parameters")
                continue
            
            operation = parts[0]
            
            if operation not in calc.tools:
                print(f"❌ Unknown operation: {operation}")
                continue
            
            try:
                tool_method = getattr(calc, operation)
                
                # Handle different parameter patterns
                if operation in ["add", "subtract", "multiply", "divide", "power", "gcd"]:
                    if len(parts) < 3:
                        print("❌ This operation requires two numbers")
                        continue
                    
                    if operation == "power":
                        result = tool_method(base=float(parts[1]), exponent=float(parts[2]))
                    elif operation == "gcd":
                        result = tool_method(a=int(parts[1]), b=int(parts[2]))
                    else:
                        result = tool_method(a=float(parts[1]), b=float(parts[2]))
                
                elif operation in ["sqrt", "abs", "factorial"]:
                    if len(parts) < 2:
                        print("❌ This operation requires one number")
                        continue
                    
                    if operation == "factorial":
                        result = tool_method(n=int(parts[1]))
                    else:
                        result = tool_method(x=float(parts[1]))
                
                elif operation == "round":
                    if len(parts) < 2:
                        print("❌ Round requires a number and optional decimal places")
                        continue
                    
                    decimals = int(parts[2]) if len(parts) > 2 else 0
                    result = tool_method(x=float(parts[1]), decimals=decimals)
                
                else:
                    print(f"❌ Interactive mode not implemented for {operation}")
                    continue
                
                print(f"✅ Result: {result}")
                
            except ValueError as e:
                print(f"❌ Invalid input: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break


async def main():
    """Run the complete calculator demo."""
    print("🚀 MCP Calculator Server Demo")
    print("=" * 70)
    print("This demo showcases the Model Context Protocol (MCP) Calculator Server")
    print("Learn how MCP tools work through practical examples!")
    print("=" * 70)
    print()
    
    # Run all demo sections
    await demo_server_info()
    await demo_basic_operations()
    await demo_advanced_operations()
    await demo_error_handling()
    
    # Ask if user wants interactive mode
    try:
        response = input("Would you like to try the interactive calculator? (y/N): ")
        if response.lower().startswith('y'):
            await interactive_calculator()
    except (KeyboardInterrupt, EOFError):
        pass
    
    print("\n🎉 Demo completed successfully!")
    print("\nNext steps:")
    print("1. Explore the calculator server code in mcp_servers/calculator_server.py")
    print("2. Try the file server demo: python demo_file_server.py")
    print("3. Start the web server: python cli.py server")
    print("4. Visit http://localhost:8000 for interactive tutorials")


if __name__ == "__main__":
    asyncio.run(main())
