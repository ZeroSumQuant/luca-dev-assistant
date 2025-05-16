"""Context store factory module.

This module provides factory functions for creating context store instances
based on configuration.
"""

import asyncio
import os
from typing import Dict, Optional

from luca_core.context.base_store import BaseContextStore
from luca_core.context.sqlite_store import SQLiteContextStore


async def create_async_context_store(
    store_type: str = "sqlite",
    db_path: Optional[str] = None,
    config: Optional[Dict] = None,
) -> BaseContextStore:
    """Create a context store instance asynchronously.

    Args:
        store_type: Type of store to create ("sqlite" or future types)
        db_path: Path to database file (for SQLite)
        config: Additional configuration dictionary

    Returns:
        An initialized context store instance
    """
    config = config or {}

    if db_path is not None:
        config["path"] = db_path

    if store_type == "sqlite":
        path = config.get("path", os.environ.get("LUCA_SQLITE_PATH", "data/context.db"))
        backup_interval = int(
            config.get("backup_interval", os.environ.get("LUCA_BACKUP_INTERVAL", "300"))
        )

        store = SQLiteContextStore(db_path=path, backup_interval=backup_interval)
    else:
        raise ValueError(f"Unsupported context store type: {store_type}")

    # Initialize the store
    await store.initialize()

    return store


def create_context_store(
    store_type: str = "sqlite",
    db_path: Optional[str] = None,
    config: Optional[Dict] = None,
) -> BaseContextStore:
    """Create a context store instance synchronously.

    This is a synchronous wrapper around create_async_context_store for convenience
    in synchronous code.

    Args:
        store_type: Type of store to create ("sqlite" or future types)
        db_path: Path to database file (for SQLite)
        config: Additional configuration dictionary

    Returns:
        An initialized context store instance
    """
    # Check if we're in an event loop
    try:
        loop = asyncio.get_running_loop()
        # We're in an event loop, so create a task and run it to completion
        return loop.run_until_complete(
            create_async_context_store(store_type, db_path, config)
        )
    except RuntimeError:
        # No event loop running, so create one with asyncio.run
        return asyncio.run(create_async_context_store(store_type, db_path, config))
