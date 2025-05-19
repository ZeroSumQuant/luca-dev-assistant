#!/bin/bash
# LUCA Git Hooks Installation Script
# Version: 1.0.0
# Updated: 2025-05-19

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔧 LUCA Git Hooks Installer${NC}"
echo -e "${YELLOW}===========================${NC}"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Not in a git repository!${NC}"
    exit 1
fi

# Get the git hooks directory
HOOKS_DIR=$(git rev-parse --git-dir)/hooks
REPO_ROOT=$(git rev-parse --show-toplevel)
SOURCE_DIR="$REPO_ROOT/hooks"

# Check if source hooks exist
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo -e "${RED}❌ ERROR: Source hooks directory not found!${NC}"
    echo -e "${RED}   Expected: $SOURCE_DIR${NC}"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Install pre-push hook
if [[ -f "$SOURCE_DIR/pre-push" ]]; then
    echo -e "${YELLOW}Installing pre-push hook...${NC}"
    
    # Check if hook already exists
    if [[ -f "$HOOKS_DIR/pre-push" ]]; then
        echo -e "${YELLOW}⚠️  WARNING: pre-push hook already exists${NC}"
        echo -e "${YELLOW}   Creating backup at: $HOOKS_DIR/pre-push.backup${NC}"
        cp "$HOOKS_DIR/pre-push" "$HOOKS_DIR/pre-push.backup"
    fi
    
    # Copy and make executable
    cp "$SOURCE_DIR/pre-push" "$HOOKS_DIR/pre-push"
    chmod +x "$HOOKS_DIR/pre-push"
    echo -e "${GREEN}✓ pre-push hook installed${NC}"
else
    echo -e "${RED}❌ ERROR: pre-push hook not found in source directory${NC}"
    exit 1
fi

echo -e "${GREEN}===========================${NC}"
echo -e "${GREEN}✅ Git hooks installation complete!${NC}"
echo -e "${GREEN}===========================${NC}"
echo
echo -e "${YELLOW}The following hooks have been installed:${NC}"
echo -e "  - pre-push: Runs safety-check.sh before allowing push"
echo
echo -e "${YELLOW}To bypass hooks in emergencies (USE WITH CAUTION):${NC}"
echo -e "  git push --no-verify"
echo
echo -e "${YELLOW}To uninstall hooks:${NC}"
echo -e "  rm $HOOKS_DIR/pre-push"