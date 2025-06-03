#!/bin/bash
# claude-startup.sh - Startup helper for Claude instances
#
# This script provides a friendly preflight checklist for Claude instances
# to ensure they have everything set up correctly before beginning work.

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      🤖 Claude Startup Helper 🤖       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Track if any checks fail
CHECKS_PASSED=true

# 1. Check directory
echo -e "${YELLOW}📍 Checking directory...${NC}"
EXPECTED_DIR="/Users/dustinkirby/Documents/GitHub/luca-dev-assistant"
if [[ "$PWD" == "$EXPECTED_DIR" ]]; then
    echo -e "${GREEN}✓ Correct directory${NC}"
else
    echo -e "${RED}✗ Wrong directory!${NC}"
    echo -e "  Current: $PWD"
    echo -e "  Expected: $EXPECTED_DIR"
    echo -e "  Run: ${GREEN}cd $EXPECTED_DIR${NC}"
    CHECKS_PASSED=false
fi
echo ""

# 2. Check virtual environment
echo -e "${YELLOW}🐍 Checking virtual environment...${NC}"
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    echo -e "${GREEN}✓ Virtual environment active${NC}"
    echo -e "  Path: $VIRTUAL_ENV"
else
    echo -e "${RED}✗ Virtual environment not active!${NC}"
    echo -e "  Run: ${GREEN}source .venv/bin/activate${NC}"
    CHECKS_PASSED=false
fi
echo ""

# 3. Check Python version
echo -e "${YELLOW}🔧 Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
if [[ "$PYTHON_VERSION" =~ ^3\.13 ]]; then
    echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3.13 required!${NC}"
    echo -e "  Current: Python $PYTHON_VERSION"
    CHECKS_PASSED=false
fi
echo ""

# 4. Check branch status
echo -e "${YELLOW}🌳 Checking branch status...${NC}"
if command -v git &> /dev/null; then
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    echo -e "  Current branch: ${BLUE}$CURRENT_BRANCH${NC}"
    
    # Run branch check
    if ./branch-check.sh 2>/dev/null; then
        # Branch check passed (output handled by script)
        :
    else
        CHECKS_PASSED=false
    fi
else
    echo -e "${RED}✗ Git not found!${NC}"
    CHECKS_PASSED=false
fi
echo ""

# 5. Quick reminders
echo -e "${YELLOW}📝 Key Reminders:${NC}"
echo -e "  • Branch naming: ${BLUE}claude-YYYY-MM-DD-topic${NC}"
echo -e "  • Always run ${GREEN}./branch-check.sh${NC} before creating branches"
echo -e "  • Run ${GREEN}./safety-check.sh${NC} before committing"
echo -e "  • Update documentation after completing work"
echo -e "  • Check ${BLUE}CLAUDE.md${NC} for complete workflow"
echo ""

# 6. Useful commands
echo -e "${YELLOW}🛠️  Useful Commands:${NC}"
echo -e "  ${GREEN}pwd && git status && git branch -a && gh pr list --limit 10${NC}"
echo -e "    ↳ Run startup ritual"
echo -e ""
echo -e "  ${GREEN}pytest -q${NC}"
echo -e "    ↳ Run tests quickly"
echo -e ""
echo -e "  ${GREEN}black . && isort . && flake8${NC}"
echo -e "    ↳ Format and lint code"
echo -e ""
echo -e "  ${GREEN}gh issue list --limit 20${NC}"
echo -e "    ↳ View open issues"
echo ""

# Final status
if [ "$CHECKS_PASSED" = true ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║    ✅ All checks passed! Ready to go!  ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo -e ""
    echo -e "${YELLOW}💡 Tip: Review CLAUDE.md for the complete workflow${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║    ⚠️  Some checks failed!             ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}"
    echo -e ""
    echo -e "${YELLOW}Please fix the issues above before proceeding.${NC}"
    echo -e "${YELLOW}Consult CLAUDE.md for detailed instructions.${NC}"
    exit 1
fi