# Contributing to LUCA Developer Assistant

Thank you for your interest in contributing to LUCA! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Pull Request Process](#pull-request-process)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Community](#community)

## Code of Conduct

We are committed to providing a friendly, safe, and welcoming environment for all contributors. By participating in this project, you agree to abide by our Code of Conduct.

## Getting Started

### Prerequisites

- Python 3.9+
- Docker
- Git

### Installation for Development

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/luca-dev-assistant.git
   cd luca-dev-assistant
   ```
3. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

We follow a feature branch workflow:

1. Always start with an up-to-date main branch:
   ```bash
   git checkout main
   git pull --ff-only origin main
   ```

2. Create a new branch for your work:
   ```bash
   git checkout -b feature-name
   ```

3. Make your changes, following our [coding standards](#coding-standards)

4. Run tests to verify your changes:
   ```bash
   make test
   ```

5. Run linting to ensure code quality:
   ```bash
   make lint
   ```

6. Commit your changes with conventional commit messages:
   ```bash
   git commit -m "feat(component): add new feature"
   ```

7. Push your branch to your fork:
   ```bash
   git push -u origin feature-name
   ```

8. Create a Pull Request against the main repository

## Pull Request Process

1. Ensure your PR has a clear description of the changes and the motivation behind them
2. Make sure all CI checks pass
3. Address any review comments
4. Once approved, your PR will be merged by a maintainer

## Coding Standards

We follow industry best practices and PEP 8 guidelines:

- Use **black** for code formatting (line length: 100)
- Use **isort** for import sorting
- Use **flake8** for linting
- Add type hints to all functions and methods
- Write docstrings for all public functions, classes, and methods
- Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages

## Testing

- Write tests for all new features and bug fixes
- Aim for high test coverage
- Tests are written using pytest
- Run the test suite with:
  ```bash
  make test
  ```

## Documentation

- Update documentation when adding or modifying features
- Keep the README.md up to date
- Add entries to docs/task_log.md for significant changes
- Create detailed handoff documents in docs/handoff/ for major features

## Community

- Join our community discussions [link to forum/chat]
- Follow our [Twitter](https://twitter.com/LUCA_AI)
- Report bugs and request features through GitHub Issues

---

Thank you for contributing to LUCA! Your efforts help improve the developer experience for QuantConnect users everywhere.
