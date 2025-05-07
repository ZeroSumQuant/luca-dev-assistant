from autogen_core.tools import FunctionTool

"""Luca Dev Assistant – main entry point.

* When called with no arguments, launches the Streamlit UI
* When called with a prompt, processes it using the agent system
* Registers safe file-I/O and Git helpers
"""

import sys
import subprocess
import os

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


def launch_ui():
    """Launch the Streamlit UI interface."""
    try:
        print("🚀 Launching Luca Dev Assistant UI...")
        app_path = os.path.join(os.path.dirname(__file__), "app", "main.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        sys.exit(1)


def process_prompt(prompt: str):
    """Process a command-line prompt using the agent system."""
    tools = build_tools()  # noqa: F841 – will be used when agent is implemented
    
    # TODO: Replace this with actual AutoGen agent orchestration
    print(f"📝 Processing prompt: {prompt}")
    print("🤖 Agent response: I'm currently in MVP mode. Please use the UI for full functionality.")
    
    # Launch UI as fallback
    print("\n🔄 Launching UI for full functionality...")
    launch_ui()


def main() -> int:
    """Entry-point invoked by cli wrapper & __main__ guard."""
    if len(sys.argv) == 1:
        # No arguments - launch UI
        launch_ui()
        return 0
    
    # Process command-line prompt
    prompt = sys.argv[1]
    process_prompt(prompt)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
