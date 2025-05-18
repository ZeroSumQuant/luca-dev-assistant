"""SQLite implementation of ContextStore.

This module provides a SQLite-based implementation of the ContextStore
interface for persistent storage of context data.
"""

import asyncio
import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

from luca_core.context.base_store import BaseContextStore
from luca_core.schemas.error import ErrorPayload, create_system_error

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class SQLiteContextStore(BaseContextStore):
    """SQLite implementation of ContextStore."""

    def __init__(self, db_path: str = "data/context.db", backup_interval: int = 300):
        """Initialize the SQLite context store.

        Args:
            db_path: Path to the SQLite database file
            backup_interval: Interval in seconds for automatic backups
        """
        self.db_path = db_path
        self.backup_interval = backup_interval
        self.conn: Optional[sqlite3.Connection] = None
        self._lock = asyncio.Lock()
        self._backup_task: Optional[asyncio.Task[None]] = None

    async def initialize(self) -> None:
        """Initialize the SQLite database.

        Creates the database file and necessary tables if they don't exist.
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Connect to the database
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # Create the metadata table
        assert self.conn is not None  # For mypy
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                namespace TEXT NOT NULL,
                model_type TEXT NOT NULL,
                key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (namespace, model_type, key)
            )
        """
        )

        # Create the data table
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS data (
                namespace TEXT NOT NULL,
                model_type TEXT NOT NULL,
                key TEXT NOT NULL,
                data TEXT NOT NULL,
                PRIMARY KEY (namespace, model_type, key)
            )
        """
        )

        # Create indices for faster queries
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_namespace ON metadata (namespace)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_model_type ON metadata (model_type)"
        )

        self.conn.commit()

        # Start the backup task
        if self.backup_interval > 0:
            self._backup_task = asyncio.create_task(self._backup_loop())

    async def close(self) -> None:
        """Close the database connection and cleanup resources."""
        if self._backup_task:
            self._backup_task.cancel()
            try:
                await self._backup_task
            except asyncio.CancelledError:
                pass
            finally:
                self._backup_task = None

        if self.conn:
            self.conn.close()
            self.conn = None

    async def _backup_loop(self) -> None:
        """Background task to periodically backup the database."""
        while True:
            try:
                await asyncio.sleep(self.backup_interval)
                await self._create_backup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in backup loop: {e}")

    async def _create_backup(self) -> None:
        """Create a backup of the database."""
        backup_dir = os.path.join(os.path.dirname(self.db_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        backup_path = os.path.join(backup_dir, f"context_{timestamp}.db")

        async with self._lock:
            # Use a new connection for the backup to avoid conflicts
            source = sqlite3.connect(self.db_path)
            dest = sqlite3.connect(backup_path)

            source.backup(dest)

            source.close()
            dest.close()

        logger.info(f"Created backup at {backup_path}")

    def _serialize_model(self, model: BaseModel) -> str:
        """Serialize a model to JSON string."""
        return model.model_dump_json()

    def _deserialize_model(self, model_cls: Type[T], data: str) -> T:
        """Deserialize a JSON string to a model instance."""
        return model_cls.model_validate_json(data)

    async def store(self, model: BaseModel, namespace: str = "default") -> None:
        """Store a model instance."""
        model_type = type(model).__name__
        key = getattr(model, "id", str(id(model)))
        now = datetime.utcnow().isoformat()

        async with self._lock:
            # Store metadata
            assert self.conn is not None, "Database not initialized"
            self.conn.execute(
                """
                INSERT OR REPLACE INTO metadata
                (namespace, model_type, key, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (namespace, model_type, key, now, now),
            )

            # Store data
            serialized = self._serialize_model(model)
            self.conn.execute(
                """
                INSERT OR REPLACE INTO data
                (namespace, model_type, key, data)
                VALUES (?, ?, ?, ?)
                """,
                (namespace, model_type, key, serialized),
            )

            self.conn.commit()

    async def fetch(
        self, model_cls: Type[T], key: str, namespace: str = "default"
    ) -> Optional[T]:
        """Fetch a model instance by key."""
        model_type = model_cls.__name__

        async with self._lock:
            assert self.conn is not None, "Database not initialized"
            cursor = self.conn.execute(
                """
                SELECT data
                FROM data
                WHERE namespace = ? AND model_type = ? AND key = ?
                """,
                (namespace, model_type, key),
            )

            row = cursor.fetchone()
            if not row:
                return None

            try:
                return self._deserialize_model(model_cls, row["data"])
            except Exception as e:
                logger.error(f"Error deserializing {model_type}: {e}")
                return None

    async def update(self, model: BaseModel, namespace: str = "default") -> None:
        """Update an existing model instance."""
        model_type = type(model).__name__
        key = getattr(model, "id", str(id(model)))
        now = datetime.utcnow().isoformat()

        async with self._lock:
            # Update metadata (only updated_at)
            assert self.conn is not None, "Database not initialized"
            self.conn.execute(
                """
                UPDATE metadata
                SET updated_at = ?
                WHERE namespace = ? AND model_type = ? AND key = ?
                """,
                (now, namespace, model_type, key),
            )

            # Replace data
            serialized = self._serialize_model(model)
            self.conn.execute(
                """
                UPDATE data
                SET data = ?
                WHERE namespace = ? AND model_type = ? AND key = ?
                """,
                (serialized, namespace, model_type, key),
            )

            self.conn.commit()

    async def delete(
        self, model_cls: Type[BaseModel], key: str, namespace: str = "default"
    ) -> None:
        """Delete a model instance."""
        model_type = model_cls.__name__

        async with self._lock:
            # Delete metadata
            assert self.conn is not None, "Database not initialized"
            self.conn.execute(
                """
                DELETE FROM metadata
                WHERE namespace = ? AND model_type = ? AND key = ?
                """,
                (namespace, model_type, key),
            )

            # Delete data
            self.conn.execute(
                """
                DELETE FROM data
                WHERE namespace = ? AND model_type = ? AND key = ?
                """,
                (namespace, model_type, key),
            )

            self.conn.commit()

    async def list(
        self,
        model_cls: Type[T],
        namespace: str = "default",
        limit: int = 100,
        offset: int = 0,
    ) -> List[T]:
        """List model instances of a specific type."""
        model_type = model_cls.__name__

        async with self._lock:
            assert self.conn is not None, "Database not initialized"
            cursor = self.conn.execute(
                """
                SELECT d.data
                FROM data d
                JOIN metadata m ON 
                    d.namespace = m.namespace AND 
                    d.model_type = m.model_type AND 
                    d.key = m.key
                WHERE d.namespace = ? AND d.model_type = ?
                ORDER BY m.updated_at DESC
                LIMIT ? OFFSET ?
                """,
                (namespace, model_type, limit, offset),
            )

            results = []
            for row in cursor:
                try:
                    model = self._deserialize_model(model_cls, row["data"])
                    results.append(model)
                except Exception as e:
                    logger.error(f"Error deserializing {model_type}: {e}")

            return results

    async def query(
        self,
        model_cls: Type[T],
        query: Dict[str, Any],
        namespace: str = "default",
        limit: int = 100,
        offset: int = 0,
    ) -> List[T]:
        """Query model instances based on criteria.

        This method uses simple filtering on the deserialized models, which is
        not efficient for large datasets. A more sophisticated implementation
        would translate the query to SQL.
        """
        models = await self.list(model_cls, namespace, limit=1000, offset=0)

        # Filter models based on the query
        filtered = []
        for model in models:
            match = True
            for key, value in query.items():
                if not hasattr(model, key) or getattr(model, key) != value:
                    match = False
                    break

            if match:
                filtered.append(model)

        # Apply limit and offset
        return filtered[offset : offset + limit]
