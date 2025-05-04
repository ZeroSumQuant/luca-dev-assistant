#!/usr/bin/env python3
"""
Luca Dev Assistant – Phase 2 core scaffold.

This version wires AutoGen’s FileTool (repo-bounded) and a
DockerTool executor (container-bounded).  For now Luca simply
echoes the prompt so we can prove the plumbing.
"""

import sys
from autogen import AssistantAgent, FileTool, DockerTool

# Tool fences
file_tool = FileTool(root_dir=".", allow_dangerous_erase=False)
docker_tool = DockerTool(work_dir="docker_exec", image="python:3.13-slim")

assistant = AssistantAgent(
    name="luca",
    system_message="You are Luca, the on-site dev assistant for ZeroSumQuant.",
    llm_config={"model": "gpt-4o-mini"},
    tools=[file_tool, docker_tool],
)

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python luca.py \"<your prompt>\"")
        return 1

    prompt = sys.argv[1]
    reply = assistant.run(prompt)
    print(reply)
    return 0

if __name__ == "__main__":
    sys.exit(main())
