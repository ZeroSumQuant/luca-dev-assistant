"""Luca Dev Assistant – minimal CLI scaffold.

* Prints a placeholder banner + usage when called with no prompt (exit 0).
* Echoes the prompt for now when one is supplied (exit 0).
* Registers safe file-I/O and Git helpers so the agent can call them later.
"""

import sys

from autogen.agentchat.tools import FunctionTool

# Project helpers
from tools.file_io import read_text, write_text
from tools.git_tools import get_git_diff, git_commit


def build_tools():
    """Return Luca's initial FunctionTool registry."""
    return [
        FunctionTool.from_defaults(read_text),
        FunctionTool.from_defaults(write_text),
        FunctionTool.from_defaults(get_git_diff),
        FunctionTool.from_defaults(git_commit),
    ]


def main() -> int:
    """Entry-point invoked by cli wrapper & __main__ guard."""
    if len(sys.argv) == 1:
        print("Placeholder: Luca ready for prompts.")
        print('Usage: python luca.py "<prompt>"')
        return 0

    prompt = sys.argv[1]
    tools = build_tools()  # noqa: F841 – used later when we wire the agent loop
    # TODO: replace this echo with an AutoGen agent call.
    print(f"Luca received prompt: {prompt}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
