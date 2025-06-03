#!/bin/bash

# Script to verify documentation is current
# Checks for task_log.md entry and handoff document for today

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get today's date
TODAY=$(date +%Y-%m-%d)
MONTH=$(date +%Y_%m)
CURRENT_MONTH=$(date +%B)

# Exit status
EXIT_STATUS=0

echo "Verifying documentation is current for $TODAY..."
echo

# Check consolidated task_log.md
if [ -f "docs/task_log.md" ]; then
    echo -e "ℹ️  Checking docs/task_log.md..."
    if grep -q "^## $TODAY" "docs/task_log.md"; then
        echo -e "${GREEN}✓ Found entry for today in task_log.md${NC}"
    else
        echo -e "${RED}✗ No entry for today in task_log.md${NC}"
        echo -e "${YELLOW}  Please add an entry for today with: ## $TODAY${NC}"
        EXIT_STATUS=1
    fi
else
    echo -e "${RED}✗ Task log not found at docs/task_log.md${NC}"
    echo -e "${YELLOW}  Please create the file and add an entry for today${NC}"
    EXIT_STATUS=1
fi

echo

# Check for handoff document
HANDOFF_PATTERN="docs/handoff/${TODAY}-*.md"
HANDOFF_FILES=$(find docs/handoff -name "${TODAY}-*.md" 2>/dev/null | head -1)

echo -e "ℹ️  Checking for handoff document..."
if [ -n "$HANDOFF_FILES" ]; then
    echo -e "${GREEN}✓ Found handoff document: $HANDOFF_FILES${NC}"
else
    echo -e "${RED}✗ No handoff document found for today${NC}"
    echo -e "${YELLOW}  Please create a handoff document at: docs/handoff/${TODAY}-1.md${NC}"
    echo -e "${YELLOW}  Use the numbering scheme: ${TODAY}-1.md, ${TODAY}-2.md, etc.${NC}"
    EXIT_STATUS=1
fi

echo

# Check for changelog.md
echo -e "ℹ️  Checking docs/handoff/changelog.md..."
if [ -f "docs/handoff/changelog.md" ]; then
    if grep -q "^#.* $TODAY" "docs/handoff/changelog.md"; then
        echo -e "${GREEN}✓ Found entry for today in changelog.md${NC}"
    else
        echo -e "${YELLOW}! No entry for today in changelog.md (optional)${NC}"
    fi
else
    echo -e "${YELLOW}! Changelog not found at docs/handoff/changelog.md (optional)${NC}"
fi

echo

# Summary
if [ $EXIT_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ All documentation checks passed!${NC}"
else
    echo -e "${RED}❌ Documentation needs updating${NC}"
    echo
    echo "To fix:"
    echo "1. Add an entry for today in docs/task_log.md"
    echo "2. Create a handoff document at docs/handoff/${TODAY}-1.md"
    echo "3. Optionally update docs/handoff/changelog.md"
fi

exit $EXIT_STATUS