# CLAUDE.md — LUCA Development Protocol

**Version:** 4.0.0  
**Updated:** 2025-05-18  
**Criticality:** Life-safety system - zero defects required

---

## 🚨 CRITICAL SAFETY CHECKS (RUN FIRST)

```bash
# Create this immediately: safety-check.sh
#!/bin/bash
set -euo pipefail

echo "🔐 Running LUCA Safety Protocol..."

# Location verification
[[ $PWD == "/Users/dustinkirby/Documents/GitHub/luca-dev-assistant" ]] || { echo "❌ Wrong directory!"; exit 1; }

# Virtual environment check  
[[ -n "${VIRTUAL_ENV:-}" ]] || { echo "❌ Virtual env not active!"; exit 1; }

# Python version check
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
[[ "$PYTHON_VERSION" =~ ^3\.13 ]] || { echo "❌ Python 3.13 required!"; exit 1; }

# Quality gates
black . && isort . && flake8 || { echo "❌ Code quality failed!"; exit 1; }

# Tests with 95% coverage (MANDATORY - NO EXCEPTIONS)
pytest --cov=luca_core --cov=app --cov=tools --cov-fail-under=95 || { echo "❌ Tests/coverage failed!"; exit 1; }

# Documentation check
if ! grep -q "$(date +%Y-%m-%d)" docs/task_log.md; then
    echo "❌ Update task log!"; exit 1
fi

echo "✅ All safety checks passed"
```

---

## 📋 MANDATORY WORKFLOW

### Every Session Start (NON-NEGOTIABLE)
```bash
cd /Users/dustinkirby/Documents/GitHub/luca-dev-assistant
source .venv/bin/activate
./claude-startup.sh  # Run helper script for comprehensive checks
pwd && git status && git branch -a && gh pr list --limit 10
```

### Before Creating New Branches (IMPORTANT)
1. Run `./branch-check.sh` - Ensure you're not behind main
2. Follow the update instructions if branch is outdated

### Before Every Commit (MANDATORY)
1. Run `./safety-check.sh` - MUST PASS
2. Update `docs/task_log.md` - NO EXCEPTIONS
3. Create `docs/handoff/YYYY-MM-DD-N.md` - REQUIRED
4. Verify all related issues are documented

---

## 🛠️ HELPER SCRIPTS FOR CLAUDE

### Available Helper Scripts
These scripts are designed to help Claude instances work more effectively:

1. **claude-startup.sh** - Preflight checklist for every session
   ```bash
   ./claude-startup.sh
   ```
   - Verifies correct directory, virtual env, Python version
   - Checks branch status automatically
   - Provides useful command reminders
   - Run this at the START of every session

2. **branch-check.sh** - Prevent merge conflicts
   ```bash
   ./branch-check.sh
   ```
   - Checks if your branch is behind main
   - Provides step-by-step update instructions
   - Run BEFORE creating new branches

3. **issue-checker.sh** - Find completed issues
   ```bash
   ./issue-checker.sh
   ```
   - Scans codebase for implemented features
   - Identifies issues that may be ready to close
   - Helps maintain accurate issue tracking

### When to Use Helper Scripts
- **Always start with**: `./claude-startup.sh`
- **Before new branches**: `./branch-check.sh`
- **During issue review**: `./issue-checker.sh`

---

## 🔧 AUTOMATION ISSUES TO CREATE

### Priority 1: Critical Safety
1. **safety-check.sh script** [✓ COMPLETED - Issue #67]
   - All quality gates in one command
   - 95% coverage enforcement (HARD REQUIREMENT)
   - Documentation verification (MANDATORY)
   - Zero-tolerance for failures

2. **Implement pre-push git hook** [✓ COMPLETED - Issue #68]
   - Prevent pushes without safety checks (ABSOLUTE BLOCK)
   - Block on test failures (NO OVERRIDE)
   - Require documentation updates (MANDATORY)
   - Auto-run safety-check.sh

3. **Makefile for standardization** [✓ COMPLETED - Issue #69]
   - Common commands: test, lint, safety, check-all
   - Consistent interface across machines
   - Reduce command errors
   - Include safety-check as default target

### Priority 2: Documentation
1. **Automated documentation checker** [✓ COMPLETED - Issue #70]
   - Verify task_log.md updated (REQUIRED)
   - Check handoff documents exist (MANDATORY)
   - Block commits without docs (ZERO TOLERANCE)
   - Enforce documentation standards

2. **Coverage report generator** [✓ COMPLETED - Issue #71]
   - Track coverage trends over time
   - Fail on ANY decrease below 95%
   - Generate badges automatically
   - Alert on coverage drops

### Priority 3: CI/CD
1. **Create GitHub Actions workflow** [✓ COMPLETED - Issue #72]
   - Run all safety checks on every push
   - Test on Python 3.13 exclusively
   - Block merge on ANY failures
   - No manual override option

2. **Dependency security scanner** [✓ COMPLETED - Issue #73]
   - Check for vulnerabilities daily
   - Automated security updates
   - Security alerts (CRITICAL PRIORITY)
   - Block deploys on vulnerabilities

---

## 📝 DOCUMENTATION FORMAT

### Task Log (docs/task_log.md)
```markdown
## YYYY-MM-DD
- **Changes**: Specific files modified
- **Tests**: New tests added  
- **Coverage**: Current percentage
- **Issues**: Problems encountered
- **Next**: Required follow-up
```

### Handoff (docs/handoff/YYYY-MM-DD-N.md)
```markdown
# Handoff: YYYY-MM-DD-N

## Completed
- Feature/fix with file paths
- Tests added (file:function)
- Documentation updated

## Status
- Working: List features
- Broken: Known issues
- Blocked: Dependencies

## Critical Notes
- Security considerations
- Breaking changes
- Performance impacts

## Next Session
- Priority tasks
- Required reviews
```

---

## 🎯 QUALITY REQUIREMENTS

- **Tests**: 95% coverage minimum (HARD REQUIREMENT)
- **Code**: Black, isort, flake8 clean (ZERO TOLERANCE)
- **Security**: Zero bandit findings (MANDATORY)
- **Types**: Mypy clean (where used)
- **Docs**: Always current (NO EXCEPTIONS)
- **Safety**: Must pass safety-check.sh

---

## 🚦 NAMING CONVENTIONS

### Files
- Python: `snake_case.py`
- Tests: `test_module_feature.py`
- Docs: `kebab-case.md`

### Code
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Branches
- Features: `feature/description`
- Fixes: `fix/issue-description`
- Claude: `claude-YYYY-MM-DD-topic`

---

## ⚠️ NEVER DO (ZERO TOLERANCE)

- Skip tests (95% coverage is MANDATORY)
- Ignore coverage drops (ANY drop blocks work)
- Commit without documentation (ALWAYS update docs)
- Push without safety checks (safety-check.sh MUST pass)
- Disable security features (LIFE-CRITICAL SYSTEM)
- Trust user input (VALIDATE EVERYTHING)
- Log sensitive data (SECURITY VIOLATION)
- Override safety protocols (NO EXCEPTIONS)
- Work without virtual environment
- Use Python < 3.13

---

## ✅ ALWAYS DO (MANDATORY)

- Run safety-check.sh (BEFORE COMMITS)
- Update documentation (EVERY CHANGE)
- Test edge cases (95% COVERAGE)
- Handle all errors (NO EXCEPTIONS)
- Validate inputs (SECURITY CRITICAL)
- Use environment variables for secrets
- Ask when uncertain
- Follow issue linking (#67-#74)
- Create handoff documents
- Maintain coverage above 95%

---

**⚠️ CRITICAL: Lives depend on this code. 95% coverage is MANDATORY. Zero defects required. No exceptions.**