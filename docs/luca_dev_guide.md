# LUCA Developer Guide

This document outlines the established practices for developing the LUCA Dev Assistant project, based on our latest work through May 11, 2025.

## Repository Structure

The LUCA project follows a structured organization of directories and files. Key components include:

- `app/` - Streamlit UI application with main interface and management pages
- `config/` - Configuration files including assistant settings
- `docker_exec/` - Docker execution environment files
- `docs/` - Documentation, handoff reports, and project logs
- `mcp_servers/` - Model Context Protocol server implementations
- `tools/` - Utility modules for file I/O, git operations, and MCP integration
- `tests/` - Test files for all project components

For a detailed and comprehensive view of the repository structure, please refer to [Repository Structure Documentation](repository-structure.md).

## Key Development Practices

### Git Workflow

1. **Branch Naming**:
   - Feature branches: `feature/name-of-feature`
   - Bugfix branches: `fix/issue-description`
   - Claude branches: `claude-YYYY-MM-DD-task-description`

2. **Commit Messages**:
   Follow the Conventional Commits format:
   ```
   <type>(<scope>): <short description>
   
   <longer description>
   
   <optional footer>
   ```

   Types:
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
   
   The module provides a simple function to format commit messages with 
   proper type, scope, description, body, and footer sections.
   ```

3. **Pull Request Flow**:
   - Create feature branch
   - Make changes and commit with conventional format
   - Push to GitHub and create PR with detailed description
   - Ensure CI passes (all tests green)
   - Squash and merge when approved

### Development Process

1. **Starting a Session**:
   ```bash
   cd /Users/dustinkirby/dev/luca-dev-assistant
   git pull --ff-only origin main
   git checkout -b claude-YYYY-MM-DD-task-description
   source .venv/bin/activate
   pytest -q  # Ensure all tests pass before beginning work
   ```

2. **Before Committing**:
   - Run tests: `pytest -q`
   - Verify linting: `black . && isort . && flake8`
   - Update task_log.md with your changes
   - Create handoff document if ending a session

3. **Dependency Management**:
   - Add dependencies to `requirements.txt`
   - Use specific versions when possible
   - Current key dependencies:
     ```
     python-dotenv==1.1.0
     PyYAML==6.0.2
     pytest==8.3.5
     pyautogen==0.9.0
     autogen-agentchat==0.5.6
     autogen-ext[docker]==0.5.6
     ```

## Important Technical Notes

### AutoGen Integration

1. **Proper Imports**: 
   AutoGen 0.5.6+ has a modular structure with different packages:
   ```python
   # Correct import for FunctionTool
   from autogen_core.tools import FunctionTool
   
   # Not: from autogen.agentchat.tools import FunctionTool
   ```

2. **Tool Registration**:
   ```python
   def build_tools():
       """Return Luca's initial FunctionTool registry."""
       return [
           FunctionTool(read_text, description="Read a UTF-8 text file"),
           FunctionTool(write_text, description="Write text to a file"),
           FunctionTool(get_git_diff, description="Return combined Git diff"),
           FunctionTool(git_commit, description="Stage and commit all changes"),
       ]
   ```

### MCP Integration

1. **Server Structure**:
   - MCP servers live in the `mcp_servers/` directory
   - Each server exposes resources, tools, or prompts via the MCP protocol
   - The `tools/mcp_client.py` module handles client-side connections to MCP servers
   - The `tools/mcp_autogen_bridge.py` bridges between MCP and AutoGen

2. **Client Usage**:
   ```python
   from tools.mcp_client import MCPClientManager
   
   # Initialize MCP client manager
   mcp_manager = MCPClientManager()
   
   # Connect to a server
   await mcp_manager.connect_stdio("filesystem", command="python", 
                                   args=["-m", "mcp_servers.filesystem_server"])
   
   # Get available tools
   tools = await mcp_manager.list_tools("filesystem")
   ```

### Documentation Standards

1. **Handoff Reports**:
   - Create a new file at `docs/handoff/YYYY-MM-DD-N.md` for each work session
   - Follow established format with sections:
     - Session Snapshot (current state)
     - What We Completed
     - Open Issues
     - Next Recommended Steps
     - Ready-Up Checklist

2. **Task Log Updates**:
   - Update `docs/task_log.md` with each completed task
   - Format: `- **HH:MM am/pm — Task name** – brief description of what was done.`

### Testing

1. **Run Tests Before Commits**:
   ```bash
   # Run all tests
   pytest -q
   
   # Run specific test file
   pytest -q tests/test_specific_file.py
   ```

2. **CI Workflow**:
   - Tests run automatically on PRs
   - Tests must pass before merging

3. **Test Hanging Issues**:
   - Add timeouts to all tests to prevent hanging in CI:
   ```python
   @pytest.mark.timeout(30)  # 30 second timeout
   def test_something():
      # Test code here
   ```
   - Set explicit timeouts for all external API calls
   - Use process isolation with pytest-forked for problematic tests

## Changelog Management

1. **Update Workflow**:
   - Located in `.github/workflows/update-changelog.md`
   - Triggered on PR merges to main
   - Uses conventional-changelog-cli to generate entries

2. **Proper Commit Messages**:
   - Essential for good changelog entries
   - Use the `changelog_helper.py` module to format commit messages

```python
from tools.changelog_helper import format_commit_message

# Example usage
message = format_commit_message(
    "feat",
    "changelog", 
    "improve commit message formatting",
    "This adds a helper module to ensure commit messages follow the Conventional Commits format.",
    "BREAKING CHANGE: None"
)
```

## Notes on AutoGen

- The project uses AutoGen framework for agent orchestration
- AutoGen has been restructured in recent versions (0.4.0+)
- Important packages:
  - `pyautogen` - Core package
  - `autogen-agentchat` - Agent chat functionality  
  - `autogen-ext` - Extensions including Docker integration
- The `[docker]` extra is required for DockerCommandLineExecutor

## Streamlit UI

1. **Application Structure**:
   - `app/main.py` - Main chat interface
   - `app/pages/agent_manager.py` - Agent configuration
   - `app/pages/mcp_manager.py` - MCP server management

2. **Running the UI**:
   ```bash
   python run_streamlit.py
   ```

3. **UI Components**:
   - Reusable components in `app/components/` directory
   - Session state management for persistent data

## Handoff Process

At the end of each development session:

1. Run tests to ensure all are passing
2. Create handoff document in `docs/handoff/YYYY-MM-DD-N.md`
3. Update task log with completed tasks
4. Commit changes with descriptive conventional commit message
5. Push branch and create PR if appropriate

This ensures that the next developer has all the context they need to continue work on the project effectively.
