# LUCA Engineering Practices & Automation Guide
**Last Updated**: June 7, 2025  
**Purpose**: Comprehensive reference for all development practices, scripts, and automations

---

## 🚀 Quick Start Commands

### Daily Development Ritual
```bash
# 1. Start your session
cd /Users/dustinkirby/Documents/GitHub/luca-dev-assistant
source .venv/bin/activate
./scripts/dev-tools/claude-startup.sh

# 2. Before creating new branches
./scripts/dev-tools/branch-check.sh

# 3. Before any commit
./scripts/dev-tools/safety-check.sh

# 4. Find completed issues
./scripts/dev-tools/issue-checker.sh
```

---

## 📋 Helper Scripts Reference

### Core Development Scripts

#### `claude-startup.sh`
**Purpose**: Preflight checklist for every session  
**Location**: `./scripts/dev-tools/claude-startup.sh`  
**What it does**:
- Verifies correct directory
- Checks virtual environment
- Validates Python version
- Shows branch status
- Lists recent PRs

#### `branch-check.sh`
**Purpose**: Prevent merge conflicts  
**Location**: `./scripts/dev-tools/branch-check.sh`  
**What it does**:
- Checks if current branch is behind main
- Provides update instructions
- Prevents working on outdated code

#### `safety-check.sh`
**Purpose**: All quality gates in one command  
**Location**: `./scripts/dev-tools/safety-check.sh`  
**What it does**:
- Runs black formatter
- Runs isort import sorter
- Runs flake8 linter
- Runs bandit security scanner
- Runs pytest with 95% coverage requirement
- Validates documentation is current

#### `issue-checker.sh`
**Purpose**: Find completed issues  
**Location**: `./scripts/dev-tools/issue-checker.sh`  
**What it does**:
- Scans codebase for implemented features
- Identifies issues ready to close
- Helps maintain accurate issue tracking

#### `validate-issue-order.py`
**Purpose**: Validate issue dependencies and ordering  
**Location**: `./scripts/dev-tools/validate-issue-order.py`  
**What it does**:
- Checks for circular dependencies
- Validates dependency order
- Ensures high priority issues are well-positioned
- Prevents dependency violations

### Code Quality Tools

#### Python Code Watchdog
```bash
# Start monitoring
./scripts/dev-tools/start-watchdog.sh

# Stop monitoring
./scripts/dev-tools/stop-watchdog.sh
```
**What it does**:
- Real-time Python syntax validation
- Import checking
- Shows errors immediately on save
- Logs to `watchdog.log`

#### Changelog Helper
**Location**: `tools/changelog_helper.py`  
**Usage**: Automatically formats commit messages
```bash
# Example usage
python tools/changelog_helper.py "feat" "core" "Add new validation system"
```

---

## 📐 Development Standards

### Code Quality Requirements
- **Test Coverage**: ≥95% (enforced by CI)
- **Linting**: Black, isort, flake8 must pass
- **Security**: Zero bandit findings at medium+ severity
- **Documentation**: Every PR needs updated task_log.md and handoff doc

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: feat, fix, docs, style, refactor, test, chore

### Branch Naming Convention
- Features: `feature/description`
- Fixes: `fix/issue-description`  
- Docs: `docs/topic`
- Claude sessions: `claude-YYYY-MM-DD-topic`

---

## 🔄 Git Workflow

### Creating a New Feature
```bash
# 1. Update main
git checkout main && git pull

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Work and test
# ... make changes ...
./scripts/dev-tools/safety-check.sh

# 4. Commit with proper message
git add .
git commit -m "$(python tools/changelog_helper.py feat core 'Add my feature')"

# 5. Push and create PR
git push -u origin feature/my-feature
gh pr create
```

### PR Requirements
1. All CI checks must pass
2. Documentation updated (task_log.md + handoff)
3. ≥95% test coverage maintained
4. No security vulnerabilities

---

## 📊 Issue Management

### Issue Priority Labels
- `P0-critical`: Immediate action required
- `P1-high`: High priority
- `P2-medium`: Medium priority  
- `P3-low`: Low priority

### Issue Dependencies
```bash
# Add dependency
gh issue edit <number> --add-label "blocked-by:#<blocker>"

# View dependencies
gh issue view <number>
```

### CTO Dependency Audit Script
```bash
# Check for dependency violations
gh issue list --state open --json number,title,labels | \
  python -c "import json,sys; [print(f'Issue #{i['number']} blocked by {b}') 
    for i in json.load(sys.stdin) 
    for l in i.get('labels',[]) 
    for b in [l['name']] if l['name'].startswith('blocked-by:#')]"
```

---

## 🧪 Testing Practices

### Running Tests
```bash
# Full test suite with coverage
pytest --cov=luca_core --cov=app --cov=tools --cov-fail-under=95

# Specific test file
pytest tests/test_specific.py -v

# With markers
pytest -m "not skip_ci"
```

### Test Organization
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Test fixtures: `tests/conftest.py`
- Coverage config: `.config/.coveragerc`

---

## 📦 Dependency Management

### Adding New Dependencies
```bash
# Add to requirements
echo "package==version" >> requirements.txt

# Development dependencies
echo "package==version" >> requirements-dev.txt

# Install in virtual environment
pip install -r requirements.txt -r requirements-dev.txt
```

### Security Scanning
```bash
# Check for vulnerabilities
safety check

# Update vulnerable packages
pip install --upgrade <package>
```

---

## 🚨 CI/CD Pipeline

### GitHub Actions Workflows
- **CI**: Runs on every push/PR
  - Python 3.13 tests
  - Coverage enforcement
  - Linting checks
  - Security scans
  
### Local CI Simulation
```bash
# Run all checks locally
./scripts/dev-tools/safety-check.sh

# Or manually
black . && isort . && flake8 && bandit -r luca_core/ && pytest
```

---

## 📝 Documentation Requirements

### Required Documentation Updates

#### Task Log (`docs/task_log.md`)
Format:
```markdown
## YYYY-MM-DD
- **Time — Title** – Description:
  - Bullet point details
  - What was changed
  - Test coverage status
```

#### Handoff Documents (`docs/handoff/YYYY-MM-DD-N.md`)
Required sections:
- `## Work Completed`
- `## Current State`  
- `## Critical Notes`
- `## Next Steps`

### Documentation Validation
```bash
# Check if docs are current
./scripts/dev-tools/verify-docs.sh

# Validate handoff format
python scripts/validate_handoff.py docs/handoff/YYYY-MM-DD-N.md
```

---

## 🎯 Development Workflow Summary

### Morning Startup
1. Run `claude-startup.sh`
2. Check open PRs: `gh pr list`
3. Review issues: `gh issue list --assignee @me`

### Before Starting Work
1. Run `branch-check.sh`
2. Create feature branch
3. Start code watchdog (optional)

### While Coding
1. Make atomic commits
2. Run tests frequently
3. Check coverage: `pytest --cov`

### Before Committing
1. Run `safety-check.sh`
2. Update documentation
3. Use changelog helper for commit messages

### After Feature Complete
1. Create PR with `gh pr create`
2. Ensure CI passes
3. Request review

---

## 🛠️ Troubleshooting

### Common Issues

#### "Virtual environment not activated"
```bash
source .venv/bin/activate
```

#### "Tests failing with import errors"
```bash
pip install -e .
```

#### "Coverage below 95%"
```bash
# Find uncovered lines
pytest --cov=luca_core --cov-report=term-missing
```

#### "Black/isort conflicts"
```bash
# Auto-fix
black . && isort .
```

---

## 📚 Additional Resources

- Architecture docs: `docs/agent-orchestration.md`
- Development memory: `docs/CLAUDE.md`
- Repository structure: `docs/repository-structure.md`
- Issue dependencies: `docs/development/issue-dependency-order-*.md`

---

## 🚀 Quick Reference Card

```bash
# Start session
./scripts/dev-tools/claude-startup.sh

# Check branch
./scripts/dev-tools/branch-check.sh

# Run all checks
./scripts/dev-tools/safety-check.sh

# Create commit
git commit -m "$(python tools/changelog_helper.py TYPE SCOPE 'Message')"

# Create PR
gh pr create

# Find issues
./scripts/dev-tools/issue-checker.sh
```

Remember: **Always run safety-check.sh before committing!**