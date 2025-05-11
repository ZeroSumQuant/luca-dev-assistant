# LUCA Repository Structure

This document provides a comprehensive overview of the LUCA Dev Assistant repository structure, describing the purpose and organization of each directory.

## Directory Structure Overview

```
/Users/dustinkirby/dev/luca-dev-assistant/
├── .env                   # Environment variables (not committed)
├── .git/                  # Git repository data
├── .github/               # GitHub workflows
│   └── workflows/         
│       ├── ci.yml         # CI workflow
│       └── update-changelog.yml  # Changelog automation
├── .gitignore             # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── .venv/                 # Python virtual environment
├── app/                   # Streamlit application UI
│   ├── components/        # Reusable UI components
│   │   └── ...
│   ├── pages/             # UI page definitions
│   │   ├── agent_manager.py  # Agent configuration UI
│   │   └── mcp_manager.py    # MCP server management UI
│   └── main.py            # Main Streamlit application entry point
├── config/
│   └── assistant_config.yaml  # Luca configuration
├── docker_exec/           # Docker execution environment files
├── docs/                  # Documentation
│   ├── handoff/           # Handoff documentation
│   │   ├── YYYY-MM-DD-N.md   # Daily handoff reports
│   │   ├── vision/        # Vision/design documents
│   │   └── changelog.md   # Auto-generated changelog
│   ├── snapshot/          # Point-in-time repository snapshots
│   ├── task_log.md        # Log of all completed tasks
│   ├── mcp-implementation-plan.md  # Plan for MCP integration
│   └── repository-structure.md  # This file - repository structure docs
├── luca.py                # Main application file
├── mcp_servers/           # Model Context Protocol servers
│   └── filesystem_server.py  # MCP server for filesystem operations
├── requirements.txt       # Project dependencies
├── run_streamlit.py       # Bootstrap script for Streamlit UI
├── scripts/               # Utility scripts
│   └── start_assistant.py # Bootstrap script
├── tests/                 # Test directory
│   ├── test_basic.py      # Basic smoke tests
│   ├── test_changelog_helper.py  # Tests for changelog helper
│   └── test_luca_*.py     # Tests for Luca functionality
└── tools/                 # Utility modules
    ├── __init__.py        # Package marker
    ├── changelog_helper.py  # Helper for commit messages
    ├── file_io.py         # File I/O utilities
    ├── git_tools.py       # Git integration utilities
    ├── mcp_client.py      # MCP client functionality
    └── mcp_autogen_bridge.py  # Bridge between MCP and AutoGen
```

## Directory Descriptions

### Root Files

- **luca.py**: Main application entry point that launches UI or processes command-line prompts
- **run_streamlit.py**: Direct Streamlit launcher script
- **requirements.txt**: Project dependencies including AutoGen, Streamlit, and testing frameworks
- **.pre-commit-config.yaml**: Pre-commit hooks configuration for code quality enforcement
- **.env**: Environment variables (not committed to repository)

### App Directory

The `app/` directory contains the Streamlit UI implementation:

- **main.py**: Main chat interface for interacting with Luca
- **pages/agent_manager.py**: Agent configuration page with tree visualization and model selection
- **pages/mcp_manager.py**: MCP server management for connecting to Model Context Protocol servers
- **components/**: Reusable UI components used across multiple pages

### Config Directory

The `config/` directory contains configuration files:

- **assistant_config.yaml**: YAML configuration for Luca, including agent and model settings

### Docker_exec Directory

The `docker_exec/` directory contains files related to Docker-based code execution:

- Contains workspace files for the Docker-based code execution sandbox

### Docs Directory

The `docs/` directory organizes project documentation:

- **handoff/**: Detailed handoff documents for development sessions
  - **YYYY-MM-DD-N.md**: Daily handoff reports (where N is the sequence number for the day)
  - **vision/**: Contains vision and design documents
  - **changelog.md**: Auto-generated changelog
- **snapshot/**: Point-in-time repository snapshots for reference
- **task_log.md**: Chronological log of completed tasks
- **mcp-implementation-plan.md**: Plan for MCP integration
- **repository-structure.md**: This file - documenting the repository structure

### MCP_servers Directory

The `mcp_servers/` directory contains Model Context Protocol servers:

- **filesystem_server.py**: MCP server for filesystem operations
- Additional MCP servers will be added here as they are developed

### Scripts Directory

The `scripts/` directory contains utility scripts:

- **start_assistant.py**: Bootstrap script for starting the assistant

### Tests Directory

The `tests/` directory contains test files for the project:

- **test_basic.py**: Basic smoke tests
- **test_changelog_helper.py**: Tests for changelog helper
- **test_luca_*.py**: Tests for Luca functionality

### Tools Directory

The `tools/` directory contains utility modules:

- **changelog_helper.py**: Helper for commit messages
- **file_io.py**: File I/O utilities (sandboxed to repo root)
- **git_tools.py**: Git integration utilities (diff and commit operations)
- **mcp_client.py**: MCP client functionality
- **mcp_autogen_bridge.py**: Bridge between MCP and AutoGen

## Development Workflow

For information about the development workflow, including branching strategy, commit message format, and pull request process, see the developer guides in the `docs/handoff/` directory.
