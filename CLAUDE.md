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
   NOTE: task_log.md is large (400+ lines) with ordering issues. Consider creating `docs/task_log_2025_05.md` for May entries.

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

## 8 Docker Guidelines

* Build locally with DOCKER_BUILDKIT=1 and --platform linux/amd64; skip Desktop-Cloud.
* Tag every image twice: one immutable tag that matches git describe --tags (e.g. v0.5.2) and the rolling tag latest.
* Push the version tag first, then latest. Allow several minutes; never wrap the push in a timeout.
* After pushing, refresh Docker Hub and confirm both tags show today's timestamp.
* Nightly: if git describe --tags differs from the value stored in .last_docker_tag, rebuild and push both tags, then update .last_docker_tag.

## 9 Testing Guidelines

* pytest-asyncio must remain in requirements.txt; CI fails without it.
* CI runs on Python 3.13—pin plugin versions that are known-good for that runtime.
* Integration tests needing a live MCP server stay skipped in CI; guard them with RUN_MCP_INTEGRATION=1.
* Maintain overall coverage ≥ 90 %. Add happy-path and targeted error-branch tests—avoid bloat.

## 10 Pre-commit and Linting

* Ensure flake8 runs in the pre-commit hook; fix or ignore violations before every push.
* Black is the authoritative formatter; let it run automatically on commit.

## 11 Nightly Backup Routine

* Run the full test suite, build and push Docker images as per section 8.
* Create a tar-gz archive of the repo.
* docker image prune -f to clear dangling layers.
* Append one journal line to ~/worklogs/YYYY-MM.txt.

## 12 Future Refactors

* Expose a public executor property on FunctionTool; migrate tests off the private _func.
* After any coverage-raising PR, bump the coverage gate in pyproject.toml so the bar never drops.

## 13 Documentation Structure

**Task Logs:**
- Primary log: `docs/task_log.md` (400+ lines, has ordering issues)
- Consider creating monthly logs: `docs/task_log_2025_05.md`, etc.
- Note: Current task_log.md has merge conflict at line 412

**Handoff Documents:**
- Location: `docs/handoff/YYYY-MM-DD-N.md`
- Create at end of each session
- Include: what was done, decisions made, next steps

**Other Documentation:**
- `/docs/repository-structure.md` - Project structure reference
- `/docs/agent-orchestration.md` - Agent system architecture
- `/docs/luca_dev_guide.md` - Development guidelines
