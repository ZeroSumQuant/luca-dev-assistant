# CLAUDE.md — LUCA Development Protocol

**Version:** 3.0.0  
**Updated:** 2025-05-17  
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

# Quality gates
black . && isort . && flake8 || { echo "❌ Code quality failed!"; exit 1; }

# Tests with 95% coverage
pytest --cov=luca_core --cov=app --cov=tools --cov-fail-under=95 || { echo "❌ Tests/coverage failed!"; exit 1; }

# Documentation check
if ! grep -q "$(date +%Y-%m-%d)" docs/task_log.md; then
    echo "❌ Update task log!"; exit 1
fi

echo "✅ All safety checks passed"
```

---

## 📋 MANDATORY WORKFLOW

### Every Session Start
```bash
cd /Users/dustinkirby/Documents/GitHub/luca-dev-assistant
source .venv/bin/activate
./safety-check.sh  # Must pass before any work
pwd && git status && git branch -a && gh pr list --limit 10
```

### Before Every Commit
1. Run `./safety-check.sh`
2. Update `docs/task_log.md`
3. Create `docs/handoff/YYYY-MM-DD-N.md`

---

## 🔧 AUTOMATION ISSUES TO CREATE

### Priority 1: Critical Safety
1. **Create safety-check.sh script**
   - All quality gates in one command
   - 95% coverage enforcement
   - Documentation verification

2. **Implement pre-push git hook**
   - Prevent pushes without safety checks
   - Block on test failures
   - Require documentation updates

3. **Add Makefile for standardization**
   - Common commands: test, lint, safety
   - Consistent interface
   - Reduce command errors

### Priority 2: Documentation
1. **Automated documentation checker**
   - Verify task_log.md updated
   - Check handoff documents exist
   - Block commits without docs

2. **Coverage report generator**
   - Track coverage trends
   - Fail on decrease below 95%
   - Generate badges

### Priority 3: CI/CD
1. **Create GitHub Actions workflow**
   - Run all safety checks
   - Test on Python 3.11
   - Block merge on failures

2. **Dependency security scanner**
   - Check for vulnerabilities
   - Automated updates
   - Security alerts

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

- **Tests**: 95% coverage minimum
- **Code**: Black, isort, flake8 clean
- **Security**: Zero bandit findings
- **Types**: Mypy clean (where used)
- **Docs**: Always current

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

## ⚠️ NEVER DO

- Skip tests
- Ignore coverage drops
- Commit without documentation
- Push without safety checks
- Disable security features
- Trust user input
- Log sensitive data

---

## ✅ ALWAYS DO

- Run safety-check.sh
- Update documentation
- Test edge cases
- Handle all errors
- Validate inputs
- Use environment variables for secrets
- Ask when uncertain

---

*Lives depend on this code. 95% coverage. Zero defects.*