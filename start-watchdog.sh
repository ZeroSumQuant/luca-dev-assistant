#!/bin/bash
# start-watchdog.sh - Start the code watchdog in the background
#
# This script starts the code watchdog to monitor Python files for errors

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if we're in the right directory
if [[ ! -d "luca_core" ]]; then
    echo -e "${RED}Error: Not in LUCA project root!${NC}"
    echo "Please run from /Users/dustinkirby/Documents/GitHub/luca-dev-assistant"
    exit 1
fi

# Check if virtual environment is active
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not active${NC}"
    echo -e "Activating .venv..."
    source .venv/bin/activate
fi

# Check if watchdog is already running
if pgrep -f "python3 tools/code_watchdog.py" > /dev/null; then
    echo -e "${YELLOW}Code watchdog is already running${NC}"
    exit 0
fi

echo -e "${GREEN}Starting code watchdog...${NC}"
echo -e "The watchdog will monitor Python files for syntax and import errors."
echo -e "To stop it, use: ${YELLOW}pkill -f 'python3 tools/code_watchdog.py'${NC}"
echo ""

# Start watchdog in background
nohup python3 tools/code_watchdog.py > watchdog.log 2>&1 &
WATCHDOG_PID=$!

# Give it a moment to start
sleep 1

# Check if it's still running
if ps -p $WATCHDOG_PID > /dev/null; then
    echo -e "${GREEN}✓ Code watchdog started successfully (PID: $WATCHDOG_PID)${NC}"
    echo -e "Log output is being written to: watchdog.log"
else
    echo -e "${RED}✗ Failed to start code watchdog${NC}"
    echo -e "Check watchdog.log for errors"
    exit 1
fi