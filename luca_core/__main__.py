"""CLI entry point for luca_core module.

This provides a command-line interface to check the status of the LUCA
system and perform other administrative tasks.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from luca_core.context import factory
from luca_core.manager.manager import LucaManager
from luca_core.registry import registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = Path.home() / ".luca" / "context.db"


def get_status(db_path: Path) -> dict:
    """Get the status of the LUCA system.

    Args:
        db_path: Path to the context database

    Returns:
        Status dictionary with system information
    """
    try:
        # Ensure the directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create context store (synchronous version)
        context_store = factory.create_context_store("sqlite", str(db_path))

        # Create manager
        manager = LucaManager(
            context_store=context_store,
            tool_registry=registry,
        )

        # Get status information
        status = {
            "status": "ready",
            "db_path": str(db_path),
            "context_store": "sqlite",
            "tools_registered": len(registry.tools),
            "version": "1.0.0",
        }

        return status

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LUCA Core CLI - Administrative interface for the LUCA system"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Get the status of the LUCA system",
    )

    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to the context database (default: {DEFAULT_DB_PATH})",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle commands
    if args.status:
        status = get_status(args.db_path)
        print(json.dumps(status))
        return 0 if status["status"] == "ready" else 1

    # If no command specified, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
