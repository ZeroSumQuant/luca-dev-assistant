#!/usr/bin/env python3
"""
Luca Dev Assistant – Phase 2 scaffold (AgentChat 0.5.6)

• Wires File-access and Docker-executor tools from the new packages:
      autogen_agentchat.tools
      autogen_ext.code_executors.docker
• For now it simply echoes the prompt so tests stay lightweight; the
  tools are instantiated but not yet invoked.
"""

import sys

from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

# removed – unused

# --- Tool fences ----------------------------------------------------------

docker_tool = DockerCommandLineCodeExecutor(
    work_dir="docker_exec",  # container workdir
    image="python:3.13-slim",  # minimal base image
)

# --------------------------------------------------------------------------


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python luca.py "<prompt>"')
        return 0

    prompt = sys.argv[1]
    print(prompt)  # simple echo; full LLM loop comes next
    return 0


if __name__ == "__main__":
    sys.exit(main())
