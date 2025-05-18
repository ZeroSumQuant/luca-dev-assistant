#!/bin/bash
# LUCA Safety Check Script
# Ensures all quality gates pass before any commit

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔐 Running LUCA Safety Protocol...${NC}"

# 1. Location verification
if [[ $PWD != "/Users/dustinkirby/Documents/GitHub/luca-dev-assistant" ]]; then
    echo -e "${RED}❌ FATAL: Wrong directory!${NC}"
    echo "Expected: /Users/dustinkirby/Documents/GitHub/luca-dev-assistant"
    echo "Actual: $PWD"
    exit 1
fi
echo -e "${GREEN}✓ Directory check passed${NC}"

# 2. Virtual environment check
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo -e "${RED}❌ FATAL: Virtual environment not activated!${NC}"
    echo "Run: source .venv/bin/activate"
    exit 1
fi
echo -e "${GREEN}✓ Virtual environment active${NC}"

# 3. Code formatting check
echo -e "${YELLOW}Running black formatter...${NC}"
if ! python3 -m black --check .; then
    echo -e "${RED}❌ Code formatting issues detected!${NC}"
    echo "Run: python3 -m black ."
    exit 1
fi
echo -e "${GREEN}✓ Black formatting passed${NC}"

# 4. Import sorting check
echo -e "${YELLOW}Running isort...${NC}"
if ! python3 -m isort --check-only .; then
    echo -e "${RED}❌ Import ordering issues detected!${NC}"
    echo "Run: python3 -m isort ."
    exit 1
fi
echo -e "${GREEN}✓ Import sorting passed${NC}"

# 5. Linting check
echo -e "${YELLOW}Running flake8...${NC}"
if ! flake8; then
    echo -e "${RED}❌ Linting errors detected!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Linting passed${NC}"

# 6. Security check
echo -e "${YELLOW}Running security scan...${NC}"
if ! bandit -c pyproject.toml -r luca_core/ -ll; then
    echo -e "${RED}❌ Security issues detected!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Security scan passed${NC}"

# 7. Tests with coverage
echo -e "${YELLOW}Running tests with coverage...${NC}"
if ! python3 -m pytest --cov=luca_core --cov=app --cov=tools --cov-fail-under=95 -q; then
    echo -e "${RED}❌ Tests failed or coverage below 95%!${NC}"
    echo -e "${YELLOW}To see detailed coverage report, run:${NC}"
    echo "pytest --cov=luca_core --cov=app --cov=tools --cov-report=term-missing"
    exit 1
fi
echo -e "${GREEN}✓ Tests passed with ≥95% coverage${NC}"

# 8. Documentation check
echo -e "${YELLOW}Checking documentation...${NC}"
TODAY=$(date +%Y-%m-%d)
if ! grep -q "$TODAY" docs/task_log.md; then
    echo -e "${RED}❌ Task log not updated for today!${NC}"
    echo "Update: docs/task_log.md"
    exit 1
fi

if ! ls docs/handoff/${TODAY}*.md >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Warning: No handoff document for today${NC}"
    echo "Create: docs/handoff/${TODAY}-1.md"
fi
echo -e "${GREEN}✓ Documentation check passed${NC}"

echo -e "${GREEN}✅ All safety checks passed! Safe to commit.${NC}"