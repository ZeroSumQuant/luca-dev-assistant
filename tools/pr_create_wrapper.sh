#!/bin/bash
# Wrapper for gh pr create that ensures documentation is complete

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔍 Pre-PR Documentation Check${NC}"
echo -e "${YELLOW}=================================${NC}"

# Run documentation validation
if ! python3 tools/validate_documentation.py; then
    echo -e "${RED}❌ Cannot create PR: Documentation incomplete!${NC}"
    echo -e "${RED}   Fix all documentation issues before creating a PR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Documentation complete! Creating PR...${NC}"
echo

# Pass through to actual gh pr create command
gh pr create "$@"