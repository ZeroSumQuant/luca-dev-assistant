#!/bin/bash
# branch-check.sh - Safety check for Claude instances
# 
# This script helps Claude instances ensure they're working on
# an up-to-date branch to prevent merge conflicts.

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 Checking branch status...${NC}"

# Fetch latest changes from origin/main without merging
git fetch origin main --quiet

# Get current branch name
CURRENT_BRANCH=$(git branch --show-current)

# Count commits behind main
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo "0")

if [ "$BEHIND" -gt 0 ]; then
    echo -e "\n${RED}⚠️  WARNING: Your branch is $BEHIND commits behind main!${NC}"
    echo -e "${RED}   Current branch: $CURRENT_BRANCH${NC}"
    echo -e ""
    echo -e "${YELLOW}📋 REQUIRED ACTIONS:${NC}"
    echo -e "1. Stash any uncommitted changes:"
    echo -e "   ${GREEN}git stash push -m \"Work in progress\"${NC}"
    echo -e ""
    echo -e "2. Switch to main branch:"
    echo -e "   ${GREEN}git checkout main${NC}"
    echo -e ""
    echo -e "3. Pull latest changes:"
    echo -e "   ${GREEN}git pull origin main${NC}"
    echo -e ""
    echo -e "4. Create new branch from updated main:"
    echo -e "   ${GREEN}git checkout -b <new-branch-name>${NC}"
    echo -e ""
    echo -e "5. Apply stash if needed:"
    echo -e "   ${GREEN}git stash pop${NC}"
    echo -e ""
    echo -e "${YELLOW}📖 IMPORTANT: Review CLAUDE.md for the complete workflow!${NC}"
    echo -e "   This ensures you follow all project protocols."
    echo -e ""
    echo -e "${RED}⛔ Do not proceed without updating your branch!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Branch is up to date with main${NC}"
    echo -e "   Current branch: $CURRENT_BRANCH"
    echo -e "   You can safely proceed with your work."
fi