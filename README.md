# LUCA · Developer Assistant

[![CI Status](https://github.com/ZeroSumQuant/luca-dev-assistant/workflows/CI/badge.svg)](https://github.com/ZeroSumQuant/luca-dev-assistant/actions/workflows/ci.yml)
[![Security](https://github.com/ZeroSumQuant/luca-dev-assistant/workflows/Security%20Scan/badge.svg)](https://github.com/ZeroSumQuant/luca-dev-assistant/actions/workflows/security.yml)
[![Coverage](https://img.shields.io/badge/coverage-97.00%-brightgreen)](https://github.com/ZeroSumQuant/luca-dev-assistant/actions)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

*A powerful general-purpose development assistant built on agent orchestration technology that helps developers across the entire software development lifecycle.* ✨🧠💻

## 🚀 Development Status

- **✅ Production-Ready Architecture**: Modular design with 95%+ test coverage
- **✅ CI/CD Pipeline**: Automated testing, linting, and security scanning on every commit
- **✅ Code Quality**: Enforced with Black, isort, Flake8, and Bandit
- **✅ Documentation**: Comprehensive docs with automated changelog generation
- **🔧 Active Development**: Regular updates and feature additions

---

## Mission

Empower developers to efficiently build, test, and ship production-grade code through **one conversational AI assistant**. LUCA guides you through the entire development process - from scaffolding new projects to writing code, testing implementations, and creating documentation. While offering broad development capabilities, LUCA also provides specialized expertise for quantitative finance applications, particularly in the QuantConnect ecosystem. 🚀📊💻

---

## Key Features

| Feature                     | Description                                                                                                          |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Adaptive Agent Architecture | LUCA dynamically adjusts its team of specialist agents based on conversation context and project needs.              |
| Intelligent Orchestration   | Behind the scenes, LUCA automatically selects and coordinates the optimal specialist agents for each task.           |
| Domain Presets              | Quickly switch between development domains (general, web, data science, quantitative finance) with a simple dropdown.|
| Modular MCP Server Design   | Plug-and-play Model Context Protocol servers for different capabilities (file system, Chroma DB, LightRAG, etc.).   |
| Strategy & project planner  | Translates plain requests ("Build a web app" / "Design a trading strategy") into step-by-step agent plans.           |
| Teacher-first UX            | Explains *why* as well as *what*; walks developers through complex workflows and best practices.                     |
| Safe local execution        | Runs unit tests and linting inside Docker before touching your repo.                                                 |
| QuantConnect Integration    | Deep integration with QuantConnect for strategy development, back-testing, and deployment.                           |
| Autogen orchestration       | Manages specialist agents (coder, tester, doc-writer) and signs off only when checks pass. 🛠️🔍✅                    |

---

## Adaptive Intelligence

LUCA's architecture transforms based on your project and conversation:

- **Seamless Context Switching**: As your conversation evolves from planning to coding to testing, LUCA adjusts its specialist team without disrupting your workflow.

- **Task-Optimized Teams**: Different projects require different expertise. Building a web app? LUCA assembles UI, backend, and deployment specialists. Creating a trading strategy? LUCA brings in algorithmic trading experts and data analysts.

- **Transparent Orchestration**: While complexity is managed behind the scenes, LUCA keeps you informed about which agents are working on your behalf and why they were selected.

---

## Extensible MCP Architecture

LUCA leverages the Model Context Protocol (MCP) to provide a highly extensible system:

- **Pre-configured Servers**: Ships with essential MCP servers enabled by default (filesystem, Chroma DB, LightRAG, Graffiti) - zero configuration required.

- **Modular Design**: Each capability is encapsulated in its own MCP server, communicating through a standardized protocol.

- **Custom Servers**: Advanced users can create, modify, or swap out MCP servers to extend LUCA's capabilities or integrate with specialized tools.

- **Server Management**: The built-in MCP Manager interface provides a simple way to enable, disable, or configure servers as needed.

This architecture allows LUCA to evolve with your needs, from simple coding assistance to complex, customized development workflows.

---

## Personalized Learning Modes

LUCA adapts its communication style to match your preferences:

- **Noob Mode**: A judgment-free zone for beginners or those learning new domains. LUCA provides comprehensive explanations, breaks down complex concepts, offers frequent checkpoints, and suggests next steps. Perfect for those who want to learn while building.

- **Pro Mode**: Streamlined for experienced developers who know what they want. LUCA focuses on efficient execution, provides concise information, and assumes familiarity with development workflows. Get more done with fewer explanations.

- **Guru Mode**: Deep knowledge unleashed. LUCA explains the "why" behind recommendations, discusses underlying principles, explores alternative approaches, and connects concepts to broader development theory. Ideal for mastering a domain rather than just using it.

Switch modes anytime through the dropdown or simply ask LUCA to "switch to Guru mode" during your conversation. Your experience, your choice.

---

## Typical Workflow

| Step | What Happens                                                                                         |
| ---- | ---------------------------------------------------------------------------------------------------- |
| 1    | **Install LUCA**.                                                                                    |
| 2    | **Ask** → "LUCA, build a React dashboard." or "LUCA, create a data pipeline for stock analysis."     |
| 3    | LUCA drafts a plan and dispatches agent jobs.                                                        |
| 4    | Code is generated, unit‑tested, lint‑clean, and committed.                                           |
| 5    | LUCA provides documentation and guidance for extending the project.                                  |
| 6    | Iterate, deploy, and maintain with LUCA's continued assistance. 🔄📤📊                                |

---

## Project Structure

```
luca-dev-assistant/
├── luca_core/          # Core agent orchestration engine
├── app/                # Streamlit UI application
├── tools/              # Utility modules (file I/O, git, MCP bridge)
├── mcp_servers/        # Model Context Protocol servers
├── tests/              # Comprehensive test suite (95%+ coverage)
├── docs/               # Documentation and handoffs
├── scripts/            # Development and utility scripts
└── config/             # Configuration files
```

---

## Quick Start

### 1 · Install

```bash
pip install lucalab
```

### 2 · Set your model key (OpenAI, Claude, or local MCP endpoint)

```bash
export OPENAI_API_KEY="sk-..."
```

### 3 · Launch LUCA

```bash
luca
```

> LUCA detects missing config, boots a project scaffold, and opens the dashboard at `http://localhost:8501`. ⚙️📂🌐

---

## Inputs

| Required              | Notes                                                                     |
| --------------------- | ------------------------------------------------------------------------- |
| API key               | Any OpenAI‑compatible endpoint; Claude or local models via MCP also work. |
| Optional pack install | `pip install lucalab[web]` adds web‑dev helpers. 🗝️📦🔌                  |

---

## Outputs

| Output           | Example                                              |
| ---------------- | ---------------------------------------------------- |
| Git commits      | `feat(api): add REST endpoint for data processing`   |
| Project scaffolds| React apps, Python services, data pipelines          |
| QC Cloud reports | JSON & equity curve image for trading strategies     |
| Web builds       | Streamlit or FastAPI app scaffold                    |
| Guidance notes   | Stepwise instructions and best‑practice tips. 📈📝📬 |

---

## Super‑powers at a Glance

| Capability          | Engine                                           |
| ------------------- | ------------------------------------------------ |
| Code read/write     | AutoGen.FileTool + Docker sandbox                |
| Secure exec         | Pytest + custom runner with resource caps        |
| Knowledge retrieval | Chroma DB + LightRAG + Graffiti                  |
| Data access         | General APIs + QuantConnect APIs + local mounts  |
| Agent orchestration | AutoGen framework with custom termination logic 🔍🧠📚  |

---

## Guardrails

| Rule                        | Rationale                                              |
| --------------------------- | ------------------------------------------------------ |
| Never reads raw keys        | Keys stay in your env; LUCA pipes without logging.     |
| Never deletes data silently | Destructive ops require `--force` or Y/N confirm.      |
| Never commits red tests     | Build & unit tests must pass before `git push`. ⛔🛡️✔️ |

---

## Use Cases

LUCA excels at a wide range of development tasks:

### General Development
- Scaffolding and building web applications (React, Vue, Angular)
- Creating Python services and APIs (FastAPI, Flask, Django)
- Building data processing pipelines
- Implementing ML models and data science workflows

### Quantitative Finance
- Developing trading strategies for QuantConnect
- Creating back-testing frameworks
- Implementing risk management systems
- Building financial data analysis tools

---

## Contributing

Pull requests welcome! Please run `make all` before submitting to ensure all checks pass. 🤝🔧📤

### Available Make Commands

- `make all` - Run full safety check (lint, test, docs)
- `make test` - Run all tests with LUCA_TESTING environment
- `make lint` - Run black, isort, flake8, and bandit
- `make safety` - Run safety-check.sh script
- `make clean` - Remove generated files and caches
- `make docs` - Check documentation is current
- `make test-docker` - Run tests in Docker container
- `make help` - Display available commands

### Git Hooks

To install git hooks that enforce safety standards:

```bash
./hooks/install.sh
```

This installs a pre-push hook that runs `safety-check.sh` before allowing pushes, ensuring:
- Tests pass with ≥95% coverage
- Code is properly formatted and linted
- Documentation is updated
- Security scans pass

See `hooks/README.md` for more details.

---

## License

MIT 📜✅⚖️