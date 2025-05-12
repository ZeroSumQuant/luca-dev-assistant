"""Luca Dev Assistant – main entry point.

* When called with no arguments, launches the Streamlit UI
* When called with a prompt, processes it using the agent system
* Uses luca_core for agent orchestration
"""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

from autogen_core.tools import FunctionTool

# Project helpers
from tools.file_io import read_text, write_text
from tools.git_tools import get_git_diff, git_commit

# Import luca_core components
from luca_core.context import factory
from luca_core.error import error_handler
from luca_core.manager.manager import LucaManager
from luca_core.registry import registry
from luca_core.schemas.agent import LearningMode
from luca_core.schemas.base import ResponseOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# DB path for context store
DB_PATH = Path(__file__).parent / "data" / "luca.db"
DB_PATH.parent.mkdir(exist_ok=True)

# Global manager instance
_manager = None


def get_manager():
    """Returns a singleton LucaManager instance."""
    global _manager
    if _manager is None:
        # Create context store
        context_store = factory.create_context_store("sqlite", str(DB_PATH))
        
        # Initialize tool registry with our existing tools
        registry.register(read_text, name="file_io.read_text", 
                        description="Read a UTF-8 text file")
        registry.register(write_text, name="file_io.write_text",
                        description="Write text to a file")
        registry.register(get_git_diff, name="git_tools.get_git_diff",
                        description="Return combined Git diff")
        registry.register(git_commit, name="git_tools.git_commit",
                        description="Stage and commit all changes")
        
        # Create manager with context store and tool registry
        _manager = LucaManager(context_store=context_store, 
                             tool_registry=registry,
                             error_handler=error_handler)
    
    return _manager


def build_tools():
    """Return Luca's initial FunctionTool registry.
    
    Used primarily for backward compatibility with existing code.
    New code should use the registry directly.
    """
    return [
        FunctionTool(read_text, description="Read a UTF-8 text file"),
        FunctionTool(write_text, description="Write text to a file"),
        FunctionTool(get_git_diff, description="Return combined Git diff"),
        FunctionTool(git_commit, description="Stage and commit all changes"),
    ]


def launch_ui():
    """Launch the Streamlit UI interface."""
    # Check if we're in testing mode - if so, don't launch UI
    if os.environ.get("LUCA_TESTING") == "1":
        print("🧪 Testing mode detected, skipping UI launch")
        return

    try:
        print("🚀 Launching Luca Dev Assistant UI...")
        app_path = os.path.join(os.path.dirname(__file__), "app", "main.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        sys.exit(1)


async def async_process_prompt(prompt: str):
    """Process a prompt asynchronously using the LucaManager."""
    manager = get_manager()
    
    # Initialize the manager if this is first run
    await manager.initialize()
    
    # Process the request through the manager
    response_options = ResponseOptions(
        learning_mode=LearningMode.PRO,
        verbose=False,
        include_agent_info=True
    )
    
    try:
        response = await manager.process_request(prompt, response_options)
        return response
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        return f"Error processing your request: {str(e)}"


def process_prompt(prompt: str, launch_ui_after=True):
    """Process a command-line prompt using the agent system."""
    # Check if we're in testing mode
    testing_mode = os.environ.get("LUCA_TESTING") == "1"
    if testing_mode:
        print("🧪 Testing mode detected in process_prompt")

    # Build tools for backward compatibility
    tools = build_tools()  # noqa: F841

    print(f"📝 Processing prompt: {prompt}")
    
    # Use the async manager to process the prompt
    try:
        # Run the async function in an event loop
        response = asyncio.run(async_process_prompt(prompt))
        print(f"🤖 Agent response: {response}")
    except Exception as e:
        logger.error(f"Error in async processing: {e}")
        print(f"🤖 Error: {str(e)}")
        print("I'm currently in fallback mode. Please try again or use the UI for full functionality.")

    # Launch UI as fallback, unless testing
    if launch_ui_after and not testing_mode:
        print("\n🔄 Launching UI for full functionality...")
        launch_ui()


def main() -> int:
    """Entry-point invoked by cli wrapper & __main__ guard."""
    # Debug: Print all environment variables to help debugging
    testing_mode = os.environ.get("LUCA_TESTING") == "1"
    print(f"🔍 LUCA_TESTING environment variable: {os.environ.get('LUCA_TESTING')}")
    print(f"🔍 Testing mode detected: {testing_mode}")

    if len(sys.argv) == 1:
        # No arguments - launch UI unless in testing mode
        if not testing_mode:
            launch_ui()
        else:
            print("🧪 Testing mode detected, skipping UI launch in no-args case")
        return 0

    # Process command-line prompt
    prompt = sys.argv[1]
    process_prompt(prompt, launch_ui_after=not testing_mode)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
