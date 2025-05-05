# Luca Dev Assistant · Task Log

## 2025-05-03
- **Project bootstrap** – created `README.md`, `.gitignore`, `requirements.txt`; activated `.venv`.
- **Bootstrap script & test** – added `scripts/start_assistant.py` and `tests/test_basic.py`.
- **Containerisation** – wrote slim `Dockerfile`; local build & run green.
- **CI online** – GitHub Actions workflow (`ci.yml`) installs deps, runs tests, builds image; first run green.
- **Image pushed** – logged in and pushed `zerosumquant/luca-dev:latest` to Docker Hub.
- **Handoff logs** – committed first hand-off to `docs/handoff/2025-05-03.md`.

## 2025-05-04
- **Automation upgrades** – added `update-changelog.yml`, `docs/handoff/changelog.md`, and initial `docs/task_log.md`.
- **Autogen stack installed** – `pyautogen` 0.9, `autogen-agentchat` & `autogen-ext[docker]` 0.5.6.
- **Luca core scaffold** – created `luca.py` with `DockerCommandLineCodeExecutor`; added `tests/test_luca_echo.py` & `tests/test_luca_smoke.py`.
- **Changelog workflow hardened** – push trigger, diff-guard, rebase-before-push, bot write-perms.
- **Pre-commit gate** – black, isort, flake8 (len 100), bandit, mypy; repo auto-formatted & lint-clean.
- **Safe file I/O** – added `tools/file_io.py`; purged deprecated `DirectoryReadTool` import.
- **Docker exec fix** – removed unsupported `network=` kw-arg from `DockerCommandLineCodeExecutor`.
- **Research deep-dive** – confirmed tool-set best practices and MCP integration roadmap.
