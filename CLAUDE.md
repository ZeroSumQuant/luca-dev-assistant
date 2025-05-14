# CLAUDE.md — LUCA Dev‑Assistant Rules (2025‑05‑12)
*This file is auto‑loaded by Claude Desktop when the **luca‑dev‑assistant** repo is opened. Follow every rule herein before writing code, running shell commands, or suggesting tasks.*

## 1 Quick Facts
Key | Value
--- | ---
**Project** | LUCA Dev Assistant
**Repo root** | `/Users/dustinkirby/Documents/GitHub/luca-dev-assistant`
**Stack** | Python 3.11 • Streamlit • AutoGen 0.5 • MCP
**Branch scheme** | `feature/…`  `fix/…`  `claude‑YYYY‑MM‑DD‑…`

## 2 Startup Ritual (run once per session)

```bash
pwd && git status && git branch -a && gh pr list --limit 10
```

```execute_command
```

*Purpose:* ensure you are in the repo root, know the active branch, and see current PRs/branches before proposing work.

## 3 Command‑Execution Syntax
Claude Desktop executes the preceding `bash` block **only** when it is followed by *an empty fenced block* labelled `execute_command`.

```bash
pytest -q
```

```execute_command
```

**Rules**
1. **One atomic step per turn.** Chain with `&&` only if output is still readable.
2. **Ask for confirmation** before destructive commands (delete, reset, deploy, DB migrate). If the user replies yes/✅, insert the `execute_command` block without further questions.
3. Use `python3` exclusively—never call bare `python`.

## 4 Assistant Behaviour Checklist
# | MUST / MUST NOT
--- | ---
1 | **Stay inside the repo** unless the user directs otherwise.
2 | **Follow KISS & DRY.** Implement only what is requested; no speculative refactors.
3 | **Add/adjust tests** in `tests/` for every new or changed function.
4 | **Provide status summaries** after discovery phases (≤ 5 lines: *What I learned → Next step*).
5 | **Ask when uncertain.** Never guess at repo state or feature intent.
6 | **Never leak secrets.** Use `os.getenv("TOKEN")` placeholders.
7 | **Document work** at session end → update `docs/task_log.md` & create `docs/handoff/YYYY‑MM‑DD‑N.md`.

## 5 Quality Gates (CI)
* `black`, `isort`, `flake8` must pass.
* `pytest -q` green, > 85 % coverage.
* `bandit` medium+ issues block merge.

Run locally before committing:

```bash
black . && isort . && flake8 && pytest -q && bandit -c pyproject.toml -r src/ -ll
```

```execute_command
```

## 6 Git & PR Workflow
1. Create a task branch (`claude-YYYY-MM-DD-topic`).
2. Use Conventional Commits: `feat(scope): subject`.
3. Squash‑merge via PR once CI is green and docs updated.

## 6.1 Git Authentication Tips

### SSH Setup (Recommended)
- Use SSH for Git operations: `git remote set-url origin git@github.com:username/repo.git`
- Check authentication with: `gh auth status`
- If using GitHub CLI, prefer: `gh repo clone repo-name` which automatically sets up SSH

### Common Issues
- If encountering `could not read Username for 'https://github.com'`, switch to SSH URLs
- Use `gh repo view --json sshUrl -q .sshUrl` to get the SSH URL for the current repo
- Set Git to remember credentials: `git config --global credential.helper cache`

## 7 AutoGen & MCP Notes
* Import tools with `from autogen_core.tools import FunctionTool`.
* Tool registry in `tools/autogen_tools.py`.
* MCP bridge in `tools/mcp_autogen_bridge.py`.

"Let all things be done decently and in order." — 1 Cor 14:40
