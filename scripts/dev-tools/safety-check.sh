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
    # Try to activate it automatically if it exists
    if [[ -f ".venv/bin/activate" ]]; then
        echo -e "${YELLOW}Activating virtual environment...${NC}"
        source .venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${RED}❌ FATAL: Virtual environment not found!${NC}"
        echo "Run: python3 -m venv .venv && source .venv/bin/activate"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Virtual environment active${NC}"
fi

# 3. Python version check
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
REQUIRED_VERSION="3.13"
if [[ ! "$PYTHON_VERSION" =~ ^$REQUIRED_VERSION ]]; then
    echo -e "${RED}❌ FATAL: Wrong Python version!${NC}"
    echo "Required: Python $REQUIRED_VERSION"
    echo "Current: Python $PYTHON_VERSION"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# 4. Code formatting check
echo -e "${YELLOW}Running black formatter...${NC}"
if ! python3 -m black --check .; then
    echo -e "${RED}❌ Code formatting issues detected!${NC}"
    echo "Run: python3 -m black ."
    exit 1
fi
echo -e "${GREEN}✓ Black formatting passed${NC}"

# 5. Import sorting check
echo -e "${YELLOW}Running isort...${NC}"
if ! python3 -m isort --check-only .; then
    echo -e "${RED}❌ Import ordering issues detected!${NC}"
    echo "Run: python3 -m isort ."
    exit 1
fi
echo -e "${GREEN}✓ Import sorting passed${NC}"

# 6. Linting check
echo -e "${YELLOW}Running flake8...${NC}"
if ! flake8 --config=.config/.flake8; then
    echo -e "${RED}❌ Linting errors detected!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Linting passed${NC}"

# 7. Security check
echo -e "${YELLOW}Running security scan...${NC}"
if ! bandit -c .config/pyproject.toml -r luca_core app tools -ll; then
    echo -e "${RED}❌ Security issues detected!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Security scan passed${NC}"

# 8. Tests with coverage
echo -e "${YELLOW}Running tests with coverage...${NC}"
if ! python3 -m pytest --cov=luca_core --cov=app --cov=tools --cov-fail-under=95 -q -m "not skip_ci" --cov-config=.coveragerc; then
    echo -e "${RED}❌ Tests failed or coverage below 95%!${NC}"
    echo -e "${YELLOW}To see detailed coverage report, run:${NC}"
    echo "pytest --cov=luca_core --cov=app --cov=tools --cov-report=term-missing -m 'not skip_ci'"
    exit 1
fi
echo -e "${GREEN}✓ Tests passed with ≥95% coverage${NC}"

# 8.1. Track coverage trends
echo -e "${YELLOW}Tracking coverage trends...${NC}"
COVERAGE_PCT=$(python3 -m coverage report | grep TOTAL | awk '{print $NF}' | sed 's/%//')
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "uncommitted")
python3 tools/coverage_tracker.py ${COVERAGE_PCT} ${COMMIT_SHA}
echo -e "${GREEN}✓ Coverage tracked: ${COVERAGE_PCT}%${NC}"

# 9. Documentation check
echo -e "${YELLOW}Checking documentation...${NC}"
if ! ./verify-docs.sh; then
    echo -e "${RED}❌ Basic documentation check failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Basic documentation check passed${NC}"

# 10. Schema validation
echo -e "${YELLOW}Validating documentation schemas...${NC}"
if ! python3 tools/validate_documentation.py; then
    echo -e "${RED}❌ Documentation schema validation failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Documentation schema validation passed${NC}"

echo -e "${GREEN}✅ All safety checks passed! Safe to commit.${NC}"