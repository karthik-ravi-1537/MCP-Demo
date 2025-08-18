# MCP Demo

Model Context Protocol tutorial project with interactive examples and working implementations.

## Features

- Interactive tutorials with hands-on exercises
- Multiple MCP servers (calculator, file system, custom examples)
- Progressive learning from beginner to advanced
- Comprehensive testing and verification scripts

## Installation

### Prerequisites
- [Homebrew](https://brew.sh/) for installing uv
- [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

### Method 1: uv

```bash
brew install uv

git clone https://github.com/karthik-ravi-1537/MCP-Demo.git
cd MCP-Demo

uv sync

source .venv/bin/activate
```

### Method 2: conda

```bash
git clone https://github.com/karthik-ravi-1537/MCP-Demo.git
cd MCP-Demo

conda env create -f environment.yml
conda activate mcp-demo
```

### Verification
```bash
python test_setup.py
```

## Quick Start

```bash
# Try standalone demos
python demo_calculator.py
python demo_file_server.py
python demo_all_servers.py

# Start interactive web server
python cli.py server --host localhost --port 8000
```

Open `http://localhost:8000` for interactive tutorials.

## Project Structure

```
MCP-Demo/
├── mcp_servers/          # MCP server implementations
├── server/               # Web application and API
├── tutorials/            # Tutorial content and progress tracking
├── tests/               # Comprehensive test suite
├── demo_*.py            # Standalone demos
└── cli.py               # Command line interface
```

## Available Examples

### Calculator Server
Basic and advanced mathematical operations with error handling.

### File System Server
Secure file operations with path traversal protection.

### Web Interface
Interactive tutorial platform with real-time MCP server interaction.

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Quick verification
python test_setup.py

# Test individual components
python -c "from mcp_servers.calculator_server import CalculatorServer; print('Calculator works')"
```

## Contributing

### Development Setup

```bash
# Clone and install with dev dependencies
uv sync --dev
source .venv/bin/activate

# Install development tools
uv pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run formatting and linting
pre-commit run --all-files
```

### Development Tools

- **ruff**: Fast Python linter and formatter
- **black**: Code formatter
- **pre-commit**: Git hooks for code quality
- **pytest**: Testing framework