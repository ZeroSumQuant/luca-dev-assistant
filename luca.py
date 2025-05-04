#!/usr/bin/env python3
"""
Luca Dev Assistant – Phase 2 scaffold

• Imports AutoGen’s FileTool & DockerTool from the correct paths
• Sets them up (they’re ready for later work)
• For now simply echoes the prompt so tests pass without an API key
"""

import sys
from autogen import AssistantAgent
from autogen.agentchat.contrib.file_tool import FileTool
from autogen.agentchat.contrib.docker_tool import DockerTool

# Tool fences (not invoked yet but wired for future use)
file_tool = FileTool(root_dir=".", allow_dangerous_erase=False)
docker_tool = DockerTool(work_dir="docker_exec", image="python:3.13-slim")

assistant = AssistantAgent(  # placeholder – not used until Phase 3
    name="luca",
    system_message="You are Luca, the on-site dev assistant for ZeroSumQuant.",
    tools=[file_tool, docker_tool],
)

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python luca.py \"<your prompt>\"")
        return 1

    prompt = sys.argv[1]
    print(prompt)             # simple echo for smoke-tests
    return 0

if __name__ == "__main__":
    sys.exit(main())
