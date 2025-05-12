# LUCA Dev Assistant - Project Overview

## Current Status (2025-05-12)

### What's Built ✅
1. **Streamlit UI MVP** - Multi-page interface with:
   - Chat interface for user interaction
   - Agent Manager for visualizing and configuring agent team
   - Model selection for each agent (GPT-4, Claude, etc.)
   - Agent tree visualization using graphviz
   - MCP Manager for Model Context Protocol server management

2. **Core Infrastructure**
   - Docker containerization
   - GitHub Actions CI/CD pipeline with robust retry mechanisms
   - Pre-commit hooks (black, isort, flake8, bandit)
   - Automatic changelog generation with race condition handling
   - Comprehensive testing setup with timeouts and proper isolation

3. **Tool Set**
   - File I/O operations (`tools/file_io.py`)
   - Git operations (`tools/git_tools.py`)
   - Changelog helper (`tools/changelog_helper.py`)
   - MCP client (`tools/mcp_client.py`) and bridge (`tools/mcp_autogen_bridge.py`)
   - Filesystem MCP server implementation

4. **Agent Architecture Design**
   - Luca (Manager)
   - Coder (Developer)
   - Tester (QA)
   - Doc Writer (Documentation)
   - Analyst (QuantConnect Specialist)

5. **Documentation**
   - Comprehensive developer guide (`docs/luca_dev_guide.md`)
   - Detailed repository structure documentation
   - GitHub CLI usage documentation
   - Robust handoff process and task logging
   - GitHub issue templates and contribution guidelines

### What Needs Implementation 🚧

#### 1. Agent Orchestration Architecture (Issue #28, HIGH PRIORITY)
- Create agent orchestration architecture document
- Define agent interaction patterns and communication flow
- Design adaptive agent architecture for dynamic team composition

#### 2. AutoGen Integration (Issue #16, HIGH PRIORITY)
- Implement agent orchestration in `luca.py`
- Set up proper agent initialization and configuration
- Define termination conditions and error handling

#### 3. UI Integration (Issue #19, HIGH PRIORITY)
- Connect Streamlit UI to AutoGen agent orchestration
- Replace chat placeholders with real agent calls
- Implement proper message handling and response streaming

#### 4. MCP Improvements (Issues #17, #18)
- Add HTTP connection support to MCP Client Manager
- Implement MCP server configuration loading from config files
- Improve organization of MCP components

#### 5. Code Quality Enhancements (Issues #22, #23, #27)
- Add type hints to key functions in tools directory
- Improve error handling in external API interactions
- Add input validation to functions processing external data

### Current Git Status
- **Active Branch**: `claude-2025-05-12-github-cli-docs`
- **Last Merged PR**: PR #33 - GitHub Issues Creation
- **Next Focus**: Issue #28 - Create agent orchestration architecture document

### Key Files to Focus On
```
/luca.py                    # Main application file needing agent orchestration
/app/main.py                # Main Streamlit chat interface needing agent integration
/tools/mcp_autogen_bridge.py  # Bridge between MCP and AutoGen
/docs/                      # Location for new architecture document
```

### Next Immediate Steps
1. Create agent orchestration architecture document (Issue #28)
2. Implement AutoGen agent orchestration in luca.py (Issue #16)
3. Connect UI to agent system (Issue #19)
4. Implement MCP HTTP connection support (Issue #17)

### Technical Decisions Made
- Streamlit for UI (chosen for rapid development)
- AutoGen for agent orchestration
- MCP for extensible tool integration
- Docker for containerization
- Pytest with timeouts for testing
- Conventional commits for changelog automation

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt  # For development

# Run Streamlit UI
python3 run_streamlit.py

# Run tests
pytest -q

# Apply linting
black . && isort . && flake8
```

### Key Dependencies
- `streamlit==1.43.0` - UI framework
- `pyautogen==0.9.0` - Core package
- `autogen-agentchat==0.5.6` - Agent chat functionality
- `autogen-ext[docker]==0.5.6` - Docker integration
- `mcp>=1.0.0` - Model Context Protocol
- `pytest-timeout==2.2.0` - Test timeout handling
- Various development tools (black, isort, flake8, bandit)

---

*Updated by Claude on 2025-05-12*