#!/bin/bash
# stop-watchdog.sh - Stop the code watchdog
#
# This script stops the running code watchdog process

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if watchdog is running
if pgrep -f "python3 tools/code_watchdog.py" > /dev/null; then
    echo -e "${YELLOW}Stopping code watchdog...${NC}"
    pkill -f "python3 tools/code_watchdog.py"
    
    # Give it a moment to stop
    sleep 1
    
    # Verify it stopped
    if pgrep -f "python3 tools/code_watchdog.py" > /dev/null; then
        echo -e "${RED}✗ Failed to stop code watchdog${NC}"
        echo -e "You may need to use: kill -9 \$(pgrep -f 'python3 tools/code_watchdog.py')"
        exit 1
    else
        echo -e "${GREEN}✓ Code watchdog stopped successfully${NC}"
    fi
else
    echo -e "${YELLOW}Code watchdog is not running${NC}"
fi