#!/bin/bash
# issue-checker.sh - Check which open issues might already be implemented
#
# This script helps identify open GitHub issues that may have already been
# completed by searching for related implementations in the codebase.

set -euo pipefail

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      📋 Issue Implementation Checker    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Create temporary file for results
REPORT_FILE=$(mktemp)

# Function to check for implementation evidence
check_implementation() {
    local issue_num=$1
    local issue_title=$2
    local evidence=""
    
    case $issue_num in
        96)
            # "Add JSON Schema validation for documentation formats"
            if [[ -d "schemas" ]] && [[ -f "tools/validate_documentation.py" ]]; then
                evidence="Found: schemas/ directory and tools/validate_documentation.py"
            fi
            ;;
        95)
            # "Add watchdog for real-time code validation"
            if [[ -f "tools/code_watchdog.py" ]]; then
                evidence="Found: tools/code_watchdog.py"
            fi
            ;;
        28)
            # "Create agent orchestration architecture document"
            if [[ -f "docs/agent-orchestration.md" ]]; then
                evidence="Found: docs/agent-orchestration.md"
            fi
            ;;
        49)
            # "LucaManager CLI skeleton"
            if [[ -f "luca_core/manager/manager.py" ]] && grep -q "class LucaManager" "luca_core/manager/manager.py" 2>/dev/null; then
                evidence="Found: LucaManager implementation in luca_core/manager/manager.py"
            fi
            ;;
        61)
            # "MCP AutoGen bridge stub"
            if [[ -f "tools/mcp_autogen_bridge.py" ]]; then
                evidence="Found: tools/mcp_autogen_bridge.py"
            fi
            ;;
        56)
            # "YAML configuration loader"
            if grep -r "yaml.safe_load\|yaml.load" --include="*.py" . 2>/dev/null | grep -q "config"; then
                evidence="Found: YAML configuration loading in codebase"
            fi
            ;;
        60)
            # "sandbox limits module"
            if [[ -f "docs/sandbox_limits.md" ]] || [[ -f "luca_core/sandbox/runner.py" ]]; then
                evidence="Found: sandbox implementation or documentation"
            fi
            ;;
        26)
            # "Implement proper sandboxing for code execution"
            if [[ -f "luca_core/sandbox/runner.py" ]] && grep -q "DockerCommandLineCodeExecutor\|sandbox" luca.py 2>/dev/null; then
                evidence="Found: DockerCommandLineCodeExecutor sandbox implementation"
            fi
            ;;
        57)
            # "Streamlit status panels"
            if [[ -d "app" ]] && find app -name "*.py" -exec grep -l "status\|panel" {} \; 2>/dev/null | grep -q .; then
                evidence="Found: Streamlit UI with potential status implementations"
            fi
            ;;
        24)
            # "Add comprehensive AutoGen agent interaction tests"
            if find tests -name "*autogen*" -o -name "*agent*" 2>/dev/null | grep -q .; then
                evidence="Found: AutoGen/agent related tests"
            fi
            ;;
    esac
    
    echo "$evidence"
}

echo -e "${YELLOW}Fetching open issues...${NC}"
echo ""

# Get open issues
ISSUES=$(gh issue list --limit 100 --state open --json number,title,labels 2>/dev/null || echo "[]")

if [[ "$ISSUES" == "[]" ]]; then
    echo -e "${RED}Failed to fetch issues. Make sure 'gh' is authenticated.${NC}"
    exit 1
fi

# Parse and check each issue
echo -e "${CYAN}Checking implementation status...${NC}"
echo -e "${CYAN}═══════════════════════════════${NC}"
echo ""

POSSIBLY_COMPLETED=()
NEEDS_VERIFICATION=()

echo "$ISSUES" | jq -r '.[] | "\(.number)|\(.title)"' | while IFS='|' read -r num title; do
    evidence=$(check_implementation "$num" "$title")
    
    if [[ -n "$evidence" ]]; then
        echo -e "${GREEN}✓ Issue #$num${NC}: $title"
        echo -e "  ${YELLOW}Evidence${NC}: $evidence"
        echo ""
        POSSIBLY_COMPLETED+=("$num|$title|$evidence")
    fi
done > "$REPORT_FILE"

# Display results
if [[ -s "$REPORT_FILE" ]]; then
    cat "$REPORT_FILE"
    
    echo -e "${BLUE}═══════════════════════════════${NC}"
    echo -e "${BLUE}Summary of Possibly Completed Issues:${NC}"
    echo ""
    
    # Count possibly completed
    COMPLETED_COUNT=$(grep -c "✓" "$REPORT_FILE" || echo 0)
    echo -e "${GREEN}Found $COMPLETED_COUNT issues that may be completed${NC}"
    
    echo ""
    echo -e "${YELLOW}💡 Next Steps:${NC}"
    echo -e "1. Review each issue's implementation"
    echo -e "2. Verify functionality matches issue requirements"
    echo -e "3. Close completed issues with: ${GREEN}gh issue close <number> --comment \"Closing as completed...\"${NC}"
    echo ""
    echo -e "${YELLOW}To investigate a specific issue:${NC}"
    echo -e "  ${GREEN}gh issue view <number>${NC}"
else
    echo -e "${YELLOW}No obviously completed issues found.${NC}"
    echo -e "This doesn't mean none are completed - manual review may be needed."
fi

# Cleanup
rm -f "$REPORT_FILE"

echo ""
echo -e "${CYAN}💡 Tip: This script checks for obvious implementations.${NC}"
echo -e "${CYAN}   Some issues may be completed in ways not detected.${NC}"