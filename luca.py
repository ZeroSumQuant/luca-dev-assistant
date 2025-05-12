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

# Import luca_core components
from luca_core.context import factory
from luca_core.error import error_handler
from luca_core.manager.manager import LucaManager, ResponseOptions
from luca_core.registry import registry
from luca_core.schemas.agent import LearningMode
# Project helpers
from tools.file_io import read_text, write_text
from tools.git_tools import get_git_diff, git_commit

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
    debug_mode = os.environ.get("LUCA_DEBUG") == "1"

    if _manager is None:
        # Ensure the database directory exists
        try:
            if debug_mode:
                print(f"🐛 Ensuring database directory exists: {DB_PATH.parent}")
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            if debug_mode:
                print(f"🐛 Database directory verified: {DB_PATH.parent.exists()}")
        except Exception as e:
            logger.error(f"Failed to create database directory: {e}")
            if debug_mode:
                print(f"🐛 Database directory creation error: {e}")
            raise RuntimeError(f"Failed to create database directory: {e}")

        # Create context store
        try:
            if debug_mode:
                print("🐛 Creating context store and manager...")

            # Check if we're already in an event loop
            try:
                loop = asyncio.get_event_loop()

                if debug_mode:
                    print("🐛 Found existing event loop")

                # We're in an event loop, use a different method to create context store
                async def create_manager():
                    try:
                        context_store = await factory.create_async_context_store(
                            "sqlite", str(DB_PATH)
                        )
                        if debug_mode:
                            print("🐛 Created async context store successfully")

                        manager = LucaManager(
                            context_store=context_store,
                            tool_registry=registry,
                            error_handler=error_handler,
                        )

                        if debug_mode:
                            print("🐛 Created LucaManager successfully")

                        return manager
                    except Exception as e:
                        logger.error(f"Error in create_manager coroutine: {e}")
                        if debug_mode:
                            print(f"🐛 Error in create_manager coroutine: {e}")
                        raise

                # Use run_coroutine_threadsafe or add_task depending on context
                if loop.is_running():
                    # Add to task queue
                    if debug_mode:
                        print("🐛 Loop is running, using run_coroutine_threadsafe")
                    future = asyncio.run_coroutine_threadsafe(create_manager(), loop)
                    _manager = future.result(timeout=10)  # Wait up to 10 seconds
                else:
                    # Run directly
                    if debug_mode:
                        print("🐛 Loop is not running, using run_until_complete")
                    _manager = loop.run_until_complete(create_manager())

            except RuntimeError:
                # No event loop, use synchronous method
                if debug_mode:
                    print("🐛 No event loop found, using synchronous context store")
                context_store = factory.create_context_store("sqlite", str(DB_PATH))

                if debug_mode:
                    print("🐛 Created synchronous context store successfully")

                _manager = LucaManager(
                    context_store=context_store,
                    tool_registry=registry,
                    error_handler=error_handler,
                )

                if debug_mode:
                    print("🐛 Created LucaManager with sync store successfully")
        except Exception as e:
            logger.error(f"Failed to create LucaManager: {e}")
            if debug_mode:
                print(f"🐛 Failed to create LucaManager: {e}")
            raise RuntimeError(f"Failed to create LucaManager: {e}")

        # Register our existing tools
        try:
            if debug_mode:
                print("🐛 Registering tools with registry...")

            registry.register(
                read_text,
                name="file_io.read_text",
                description="Read a UTF-8 text file",
            )
            registry.register(
                write_text,
                name="file_io.write_text",
                description="Write text to a file",
            )
            registry.register(
                get_git_diff,
                name="git_tools.get_git_diff",
                description="Return combined Git diff",
            )
            registry.register(
                git_commit,
                name="git_tools.git_commit",
                description="Stage and commit all changes",
            )

            if debug_mode:
                print("🐛 Successfully registered all tools")
        except Exception as e:
            logger.error(f"Failed to register tools: {e}")
            if debug_mode:
                print(f"🐛 Failed to register tools: {e}")
            # We'll continue even if tool registration fails

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
    debug_mode = os.environ.get("LUCA_DEBUG") == "1"

    try:
        # Get the manager instance
        if debug_mode:
            print("🐛 Getting manager instance...")

        manager = get_manager()

        # Initialize the manager if this is first run
        if debug_mode:
            print("🐛 Initializing manager...")

        try:
            await manager.initialize()
            if debug_mode:
                print("🐛 Manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing manager: {e}")
            if debug_mode:
                print(f"🐛 Manager initialization error: {e}")
            return f"LucaString: I encountered an error during initialization: {str(e)}"

        # Process the request through the manager
        if debug_mode:
            print("🐛 Setting up response options...")

        # Get user preferences for learning mode (default to PRO)
        try:
            user_prefs = await manager.context_store.get_user_preferences()
            learning_mode = user_prefs.learning_mode
        except Exception:
            learning_mode = LearningMode.PRO

        if debug_mode:
            print(f"🐛 Using learning mode: {learning_mode}")

        response_options = ResponseOptions(
            learning_mode=learning_mode,
            verbose=debug_mode,
            include_agent_info=debug_mode,
        )

        if debug_mode:
            print(f"🐛 Processing request with manager: {prompt[:50]}...")

        # Process the request and handle any errors
        try:
            response = await manager.process_request(prompt, response_options)
            if debug_mode:
                print(
                    f"🐛 Request processed successfully, response length: {len(response)}"
                )
            return f"LucaString: {response}"
        except Exception as e:
            logger.error(f"Error processing prompt: {e}")
            if debug_mode:
                print(f"🐛 Error processing prompt: {e}")
            return f"LucaString: I encountered an error while processing your request: {str(e)}"
    except Exception as e:
        # Catch-all for any unexpected errors
        logger.error(f"Unexpected error in async_process_prompt: {e}")
        if debug_mode:
            print(f"🐛 Unexpected error in async_process_prompt: {e}")
        return f"LucaString: I encountered an unexpected error: {str(e)}"


def process_prompt(prompt: str, launch_ui_after=True):
    """Process a command-line prompt using the agent system."""
    # Check if we're in testing mode
    testing_mode = os.environ.get("LUCA_TESTING") == "1"
    skip_async_mode = os.environ.get("LUCA_SKIP_ASYNC") == "1"
    debug_mode = os.environ.get("LUCA_DEBUG") == "1"

    if testing_mode:
        print("🧪 Testing mode detected in process_prompt")
    if debug_mode:
        print("🐛 Debug mode detected in process_prompt")
        print(f"🐛 Current working directory: {os.getcwd()}")
        print(f"🐛 Database path: {DB_PATH}")
        print(f"🐛 Prompt: {prompt}")
    if skip_async_mode:
        print("⏭️ Skip async mode detected - bypassing LucaManager")

    # Build tools for backward compatibility
    tools = build_tools()  # noqa: F841
    if debug_mode:
        print(f"🐛 Built {len(tools)} tools")

    print(f"📝 Processing prompt: {prompt}")

    # For testing mode with skip_async, provide simplified response
    if testing_mode and skip_async_mode:
        print(
            f"🤖 Agent response: LucaString: Processed '{prompt}' in testing mode (skipped async)"
        )
        return

    # Use the async manager to process the prompt
    try:
        if debug_mode:
            print("🐛 Attempting to process with async manager...")

        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            if debug_mode:
                print("🐛 Using existing event loop")

            # We're in an event loop, so create a task
            task = asyncio.create_task(async_process_prompt(prompt))

            if debug_mode:
                print("🐛 Created task, waiting for completion...")

            # For synchronous behavior, wait for the task to complete
            # We can't use await here as this is not an async function
            response = loop.run_until_complete(task)

        except RuntimeError:
            if debug_mode:
                print("🐛 No event loop found, creating new one")

            # No event loop running, so create one with asyncio.run
            response = asyncio.run(async_process_prompt(prompt))

        # Print the response
        if response.startswith("LucaString: "):
            # Extract the actual response text
            response_text = response[len("LucaString: ") :]
            print(f"🤖 {response_text}")
        else:
            # Just print the raw response
            print(f"🤖 {response}")

    except Exception as e:
        logger.error(f"Error in async processing: {e}")
        if debug_mode:
            print(f"🐛 Error in async processing: {e}")
            import traceback

            traceback.print_exc()

        print(f"🤖 Error: {str(e)}")
        print(
            "I'm currently in fallback mode. Please try again or use the UI for full functionality."
        )

    # Launch UI as fallback, unless testing
    if launch_ui_after and not testing_mode:
        print("\n🔄 Launching UI for full functionality...")
        launch_ui()


def main() -> int:
    """Entry-point invoked by cli wrapper & __main__ guard."""
    # Set up environment variables and debugging
    testing_mode = os.environ.get("LUCA_TESTING") == "1"
    debug_mode = os.environ.get("LUCA_DEBUG") == "1"
    skip_async_mode = os.environ.get("LUCA_SKIP_ASYNC") == "1"

    # Set up logging based on environment
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled - verbose logging activated")
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.setLevel(logging.INFO)

    # Print environment information for debugging
    print(f"🔍 LUCA_TESTING environment variable: {os.environ.get('LUCA_TESTING')}")
    print(f"🔍 Testing mode detected: {testing_mode}")

    if debug_mode:
        print(f"🔍 Debug mode detected: {debug_mode}")
        print(f"🔍 Skip async mode: {skip_async_mode}")
        print(f"🔍 Python version: {sys.version}")
        print(f"🔍 Current directory: {os.getcwd()}")
        print(f"🔍 Database path: {DB_PATH}")

        # Print additional libraries information
        try:
            import autogen_core

            print(f"🔍 AutoGen Core version: {autogen_core.__version__}")
        except (ImportError, AttributeError):
            print("🔍 AutoGen Core version: Unknown")

        try:
            import streamlit

            print(f"🔍 Streamlit version: {streamlit.__version__}")
        except (ImportError, AttributeError):
            print("🔍 Streamlit version: Unknown")

    # Check for data directory and create if needed
    if not DB_PATH.parent.exists():
        try:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created data directory at {DB_PATH.parent}")
            if debug_mode:
                print(f"🔍 Created data directory at {DB_PATH.parent}")
        except Exception as e:
            logger.error(f"Failed to create data directory: {e}")
            if debug_mode:
                print(f"🔍 Error creating data directory: {e}")
            print(f"❌ Error: Could not create data directory: {e}")
            return 1

    # Process based on arguments
    if len(sys.argv) == 1:
        # No arguments - launch UI unless in testing mode
        if not testing_mode:
            try:
                launch_ui()
            except Exception as e:
                logger.error(f"Error launching UI: {e}")
                if debug_mode:
                    print(f"🔍 Error launching UI: {e}")
                    import traceback

                    traceback.print_exc()
                print(f"❌ Error launching UI: {e}")
                return 1
        else:
            print("🧪 Testing mode detected, skipping UI launch in no-args case")
        return 0

    # Process command-line prompt
    try:
        prompt = sys.argv[1]
        process_prompt(prompt, launch_ui_after=not testing_mode)
        return 0
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        if debug_mode:
            print(f"🔍 Error processing prompt: {e}")
            import traceback

            traceback.print_exc()
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
