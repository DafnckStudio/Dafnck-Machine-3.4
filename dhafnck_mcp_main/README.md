# dhafnck_mcp: Advanced MCP Server Framework

[![PyPI version](https://badge.fury.io/py/dhafnck_mcp.svg)](https://badge.fury.io/py/dhafnck_mcp)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/pypi/pyversions/dhafnck_mcp.svg)](https://pypi.org/project/dhafnck_mcp)
[![Test Coverage](https://img.shields.io/badge/coverage-77%25-yellow.svg)](#)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)

**`dhafnck_mcp`** is a high-performance, asynchronous-first server framework for the Model Context Protocol (MCP). It provides a complete solution for building robust, scalable, and type-safe MCP servers in Python, with a special focus on advanced task management and multi-agent orchestration.

Built with a clean, Domain-Driven Design (DDD) architecture, `dhafnck_mcp` makes it easy to expose complex business logic to AI agents through the MCP standard, enabling seamless human-AI collaboration and automation.

## ✨ Key Features

- **Asynchronous Core**: Built on modern Python `asyncio` for high-performance, non-blocking I/O.
- **Type-Safe by Design**: Fully type-annotated codebase, validated with `pyright` for robust, error-free development.
- **Domain-Driven Design (DDD)**: A clean, layered architecture that separates business logic from infrastructure, making the system easy to maintain, test, and extend.
- **Integrated Task Management**: A powerful, built-in task management system with support for projects, tasks, subtasks, dependencies, and priorities.
- **Multi-Agent Orchestration**: Tools for managing teams of AI agents, assigning them to workflows, and orchestrating their collaboration.
- **Extensible Plugin System**: Easily add new tools, resources, and prompts to extend the server's capabilities.
- **Comprehensive Testing**: A robust test suite with 77% code coverage ensures reliability and stability.
- **Modern Tooling**: Uses `uv` for dependency management, `ruff` for linting, and `pytest` for testing.

## 🏗️ Architecture Overview

`dhafnck_mcp` is built on a Domain-Driven Design (DDD) architecture, which organizes the code into four distinct layers:

1.  **Domain**: The core of the application, containing the business logic, entities, and rules. This layer is completely independent of any external frameworks or infrastructure.
2.  **Application**: Orchestrates the domain layer to perform application-specific tasks and use cases.
3.  **Infrastructure**: Provides implementations for external-facing services like databases, file systems, and third-party APIs.
4.  **Interface**: Exposes the application's functionality to the outside world, in this case, through the Model Context Protocol (MCP).

This clean separation of concerns makes the `dhafnck_mcp` framework highly modular, testable, and maintainable. For more details, see the [DDD Structure Document](.cursor/rules/dhafnck_mcp_main/ddd-structure.mdc).

## 🚀 Getting Started

### Prerequisites

-   Python 3.10+
-   `uv` (recommended for dependency management)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dhafnck/dhafnck_mcp.git
    cd dhafnck_mcp_main
    ```

2.  **Install dependencies:**
    Using `uv`:
    ```bash
    uv sync
    ```
    Or using `pip`:
    ```bash
    pip install -e .
    ```

### Running the Server

You can start the `dhafnck_mcp` server using the built-in CLI:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the server
dhafnck_mcp serve
```

This will start the MCP server on `127.0.0.1:8000`.

## ⚙️ Usage

The `dhafnck_mcp` server exposes its functionality through a set of MCP tools that can be called by any MCP-compliant client. The primary tools are:

-   `manage_project`: For creating and managing multi-agent projects.
-   `manage_task`: For all core task lifecycle operations.
-   `manage_subtask`: For hierarchical task management.
-   `manage_agent`: For registering and coordinating AI agents.
-   `call_agent`: For retrieving agent-specific configurations.

For a complete list of tools and their usage, please refer to the project's internal documentation.

## 🧪 Testing

The project includes a comprehensive test suite. To run the tests:

1.  **Install development dependencies:**
    ```bash
    uv sync --dev
    ```

2.  **Run the test suite:**
    ```bash
    pytest
    ```

3.  **Check test coverage:**
    ```bash
    pytest --cov=src/fastmcp
    ```

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and create a pull request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details. 