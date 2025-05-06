from autogen_core.tools import FunctionTool

"""Luca Dev Assistant – minimal CLI scaffold.

* Prints a placeholder banner + usage when called with no prompt (exit 0).
* Echoes the prompt for now when one is supplied (exit 0).
* Registers safe file-I/O and Git helpers so the agent can call them later.
"""

import sys

# Project helpers
from tools.file_io import read_text, write_text
from tools.git_tools import get_git_diff, git_commit


def build_tools():
    """Return Luca's initial FunctionTool registry."""
    return [
        FunctionTool(read_text, description="Read a UTF-8 text file"),
        FunctionTool(write_text, description="Write text to a file"),
        FunctionTool(get_git_diff, description="Return combined Git diff"),
        FunctionTool(git_commit, description="Stage and commit all changes"),
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
