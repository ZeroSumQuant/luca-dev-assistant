# Contributing to LUCA Dev Assistant

Thank you for your interest in contributing to LUCA! This document outlines the process for contributing to the project and helps you get started quickly.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.11 or later
- Git
- Docker (for running containerized components)

### Setting Up Your Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/ZeroSumQuant/luca-dev-assistant.git
   cd luca-dev-assistant
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Install runtime and CI dependencies
   python3 -m pip install -r requirements.txt
   
   # Install development dependencies
   python3 -m pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Run the tests to verify your setup**
   ```bash
   pytest -q
   ```

## Development Workflow

### Creating a New Feature or Fixing a Bug

1. **Create a new branch**
   - For features: `feature/name-of-feature`
   - For bugfixes: `fix/issue-description`
   - For ongoing Claude-assisted work: `claude-YYYY-MM-DD-task-description`

2. **Make your changes**
   - Follow the code style guidelines enforced by Black, isort, and flake8
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   - Run `pytest -q` to ensure all tests pass
   - Run linting with `black . && isort . && flake8`

4. **Update the task log**
   - Add an entry to `docs/task_log.md` describing your changes

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages:

```
<type>(<scope>): <short description>

<longer description>

<optional footer>
```

Types include:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting changes
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding or modifying tests
- `chore`: Changes to build process or auxiliary tools

Example:
```
feat(changelog): add conventional commits helper

This commit adds a helper module to ensure commit messages follow the
Conventional Commits format, which improves the quality of the generated
changelog.
```

You can use the `tools/changelog_helper.py` module to help format commit messages:

```python
from tools.changelog_helper import format_commit_message

message = format_commit_message(
    "feat",
    "changelog",
    "improve commit message formatting",
    "This adds a helper module to ensure commit messages follow the Conventional Commits format."
)
```

## Pull Request Process

1. **Create a pull request on GitHub**
   - Use a clear and descriptive title
   - Reference any related issues
   - Fill out the PR template with details about your changes

2. **Wait for CI to complete**
   - All tests must pass
   - Linting must pass
   - Docker build must succeed

3. **Address review feedback**
   - Make requested changes
   - Push additional commits to your branch

4. **Squash and merge**
   - Once approved, your PR will be squashed and merged into the main branch
   - The changelog will be automatically updated based on your commit messages

## Testing

### Running Tests

```bash
# Run all tests
pytest -q

# Run specific tests
pytest -q tests/test_specific_file.py

# Run tests with timeout
pytest --timeout=60 --timeout_method=thread
```

### Writing Tests

- All test files should be in the `tests/` directory
- Test files should be named `test_*.py`
- Test functions should be named `test_*`
- Use pytest fixtures for setup and teardown
- Add appropriate timeouts to prevent hanging in CI

### AutoGen Mocking Behavior

By default, tests run without AutoGen's global mock mode. Mark a test with `@pytest.mark.autogen_mock` if it depends on AutoGen's fake LLM/tool responses. CI runs the suite twice: once for mocked tests, once for real-execution tests.

```python
# For tests that need AutoGen mocking
import pytest

pytestmark = pytest.mark.autogen_mock  # Marks all tests in the module

# Or mark individual tests
@pytest.mark.autogen_mock
def test_something_with_autogen():
    pass
```

## Documentation

### Types of Documentation

- **Code Documentation**: Docstrings and comments in the code
- **Developer Guide**: `docs/luca_dev_guide.md` for detailed internal documentation
- **Handoff Reports**: `docs/handoff/YYYY-MM-DD-N.md` for session documentation
- **Task Log**: `docs/task_log.md` for chronological tracking of work

### Documentation Standards

1. **All functions should have docstrings**
   ```python
   def function_name(param1, param2):
       """Short description of what the function does.
       
       Args:
           param1: Description of param1
           param2: Description of param2
           
       Returns:
           Description of return value
       """
   ```

2. **Update repository structure documentation when making structural changes**
   - Modify `docs/repository-structure.md` when adding/removing directories or files

3. **Create handoff reports for development sessions**
   - Follow the established format in `docs/handoff/`

## Issue Reporting

### Bug Reports

When reporting a bug, please include:
- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment information (OS, Python version, etc.)

Use the bug report template provided when creating a new issue.

### Feature Requests

When requesting a feature, please include:
- A clear and descriptive title
- A detailed description of the proposed feature
- Any relevant context or use cases
- Priority and impact assessment

Use the feature request template provided when creating a new issue.

### Technical Debt

When reporting technical debt, please include:
- A clear description of what needs improvement
- The current implementation
- Your proposed improvement
- Risk assessment (risk level, effort estimate, areas affected)

Use the technical debt template provided when creating a new issue.

---

## Detailed Technical Documentation

For more detailed information about the project's architecture, implementation details, and development practices, please refer to the [Developer Guide](docs/luca_dev_guide.md).

---

Thank you for contributing to LUCA Dev Assistant! 🚀
