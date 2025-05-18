"""
Context storage system for LUCA.

This module implements the SQLite-backed ContextStore, providing persistent
storage for conversations, messages, tasks, and other context data.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

from pydantic import BaseModel

from ..schemas import (
    Conversation,
    Message,
    MetricRecord,
    Project,
    Task,
    TaskResult,
    TaskStatus,
    UserPreferences,
)

# Type variable for generic context store methods
T = TypeVar("T", bound=BaseModel)


class ContextStore:
    """
    Persistent shared memory across conversations and sessions.

    This class implements storage and retrieval of various models needed for
    maintaining context in the LUCA system. It uses SQLite as a backend for
    zero-config, ACID-compliant persistence.
    """

    def __init__(self, db_path: str = "data/context.db"):
        """
        Initialize the context store with the specified database path.

        Args:
            db_path: Path to the SQLite database file. Default: "data/context.db"
        """
        self.db_path = db_path
        self._ensure_db_exists()
        self._setup_tables()

    def _ensure_db_exists(self) -> None:
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def _setup_tables(self) -> None:
        """Set up the database tables if they don't exist."""
        with self._get_connection() as conn:
            # Create tables for different model types
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    conversation_id TEXT,
                    timestamp REAL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    project_id TEXT,
                    timestamp REAL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    conversation_id TEXT,
                    status TEXT,
                    timestamp REAL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_results (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp REAL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    timestamp REAL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    timestamp REAL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp REAL
                )
            """
            )

            # Create indices for faster lookups
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages (conversation_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_conversation ON tasks (conversation_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_conversations_project ON conversations (project_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_task_results_task ON task_results (task_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_task ON metrics (task_id)"
            )

    def store_message(
        self, message: Message, conversation_id: Optional[str] = None
    ) -> str:
        """
        Store a message in the context store.

        Args:
            message: The message to store
            conversation_id: Optional ID of the conversation this message belongs to

        Returns:
            The ID of the stored message
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO messages (id, data, conversation_id, timestamp) VALUES (?, ?, ?, ?)",
                (
                    message.id,
                    message.model_dump_json(),
                    conversation_id,
                    datetime.utcnow().timestamp(),
                ),
            )
        return message.id

    def get_message(self, message_id: str) -> Optional[Message]:
        """
        Retrieve a message by its ID.

        Args:
            message_id: The ID of the message to retrieve

        Returns:
            The message if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data FROM messages WHERE id = ?", (message_id,)
            )
            row = cursor.fetchone()
            if row:
                return Message.model_validate_json(row[0])
            return None

    def store_conversation(self, conversation: Conversation) -> str:
        """
        Store a conversation in the context store.

        Args:
            conversation: The conversation to store

        Returns:
            The ID of the stored conversation
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO conversations (id, data, project_id, timestamp) VALUES (?, ?, ?, ?)",
                (
                    conversation.id,
                    conversation.model_dump_json(),
                    conversation.project_id,
                    datetime.utcnow().timestamp(),
                ),
            )
        return conversation.id

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation to retrieve

        Returns:
            The conversation if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data FROM conversations WHERE id = ?", (conversation_id,)
            )
            row = cursor.fetchone()
            if row:
                return Conversation.model_validate_json(row[0])
            return None

    def store_task(self, task: Task, conversation_id: Optional[str] = None) -> str:
        """
        Store a task in the context store.

        Args:
            task: The task to store
            conversation_id: Optional ID of the conversation this task belongs to

        Returns:
            The ID of the stored task
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tasks (id, data, conversation_id, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                (
                    task.id,
                    task.model_dump_json(),
                    conversation_id,
                    task.status,
                    datetime.utcnow().timestamp(),
                ),
            )
        return task.id

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The task if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT data FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return Task.model_validate_json(row[0])
            return None

    def store_task_result(self, result: TaskResult) -> str:
        """
        Store a task result in the context store.

        Args:
            result: The task result to store

        Returns:
            The ID of the task associated with the result
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO task_results (id, task_id, data, timestamp) VALUES (?, ?, ?, ?)",
                (
                    f"result_{result.task_id}",
                    result.task_id,
                    result.model_dump_json(),
                    datetime.utcnow().timestamp(),
                ),
            )
        return result.task_id

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """
        Retrieve a task result by its task ID.

        Args:
            task_id: The ID of the task whose result to retrieve

        Returns:
            The task result if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data FROM task_results WHERE task_id = ?", (task_id,)
            )
            row = cursor.fetchone()
            if row:
                return TaskResult.model_validate_json(row[0])
            return None

    def store_project(self, project: Project) -> str:
        """
        Store a project in the context store.

        Args:
            project: The project to store

        Returns:
            The ID of the stored project
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO projects (id, data, timestamp) VALUES (?, ?, ?)",
                (project.id, project.model_dump_json(), datetime.utcnow().timestamp()),
            )
        return project.id

    def get_project(self, project_id: str) -> Optional[Project]:
        """
        Retrieve a project by its ID.

        Args:
            project_id: The ID of the project to retrieve

        Returns:
            The project if found, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data FROM projects WHERE id = ?", (project_id,)
            )
            row = cursor.fetchone()
            if row:
                return Project.model_validate_json(row[0])
            return None

    def store_user_preferences(
        self, preferences: UserPreferences, user_id: str = "default"
    ) -> str:
        """
        Store user preferences in the context store.

        Args:
            preferences: The user preferences to store
            user_id: The ID of the user (defaults to "default")

        Returns:
            The ID used to store the preferences
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO user_preferences (id, data, timestamp) VALUES (?, ?, ?)",
                (user_id, preferences.model_dump_json(), datetime.utcnow().timestamp()),
            )
        return user_id

    def get_user_preferences(self, user_id: str = "default") -> UserPreferences:
        """
        Retrieve user preferences.

        Args:
            user_id: The ID of the user (defaults to "default")

        Returns:
            The user preferences if found, default preferences otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data FROM user_preferences WHERE id = ?", (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return UserPreferences.model_validate_json(row[0])
            return UserPreferences()  # Return default preferences if not found

    def store_metric(self, metric: MetricRecord) -> str:
        """
        Store a metric record in the context store.

        Args:
            metric: The metric record to store

        Returns:
            The ID of the stored metric record
        """
        metric_id = f"metric_{metric.task_id}_{datetime.utcnow().timestamp()}"
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO metrics (id, task_id, data, timestamp) VALUES (?, ?, ?, ?)",
                (
                    metric_id,
                    metric.task_id,
                    metric.model_dump_json(),
                    datetime.utcnow().timestamp(),
                ),
            )
        return metric_id

    def get_metrics_for_task(self, task_id: str) -> List[MetricRecord]:
        """
        Retrieve all metric records for a task.

        Args:
            task_id: The ID of the task

        Returns:
            A list of metric records for the task
        """
        metrics = []
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data FROM metrics WHERE task_id = ?", (task_id,)
            )
            for row in cursor:
                metrics.append(MetricRecord.model_validate_json(row[0]))
        return metrics

    def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """
        Retrieve all messages for a conversation.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            A list of messages in the conversation, ordered by timestamp
        """
        messages = []
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data FROM messages WHERE conversation_id = ? ORDER BY timestamp",
                (conversation_id,),
            )
            for row in cursor:
                messages.append(Message.model_validate_json(row[0]))
        return messages

    def get_project_conversations(self, project_id: str) -> List[Conversation]:
        """
        Retrieve all conversations for a project.

        Args:
            project_id: The ID of the project

        Returns:
            A list of conversations in the project, ordered by timestamp
        """
        conversations = []
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT data FROM conversations WHERE project_id = ? ORDER BY timestamp",
                (project_id,),
            )
            for row in cursor:
                conversations.append(Conversation.model_validate_json(row[0]))
        return conversations

    def get_active_tasks(self) -> List[Task]:
        """
        Retrieve all active (pending or in_progress) tasks.

        Returns:
            A list of active tasks, ordered by priority (descending) and then timestamp
        """
        tasks = []
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT data FROM tasks 
                WHERE status IN ('pending', 'in_progress') 
                ORDER BY status, timestamp
                """
            )
            for row in cursor:
                task = Task.model_validate_json(row[0])
                tasks.append(task)

        # Sort by created_at since Task doesn't have priority field
        return sorted(tasks, key=lambda t: t.created_at)

    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update the status of a task.

        Args:
            task_id: The ID of the task to update
            status: The new status ("pending", "in_progress", "completed", or "failed")

        Returns:
            True if the task was updated, False if the task was not found
        """
        task = self.get_task(task_id)
        if not task:
            return False

        # Update the task status directly since update_status method doesn't exist
        task.status = TaskStatus(status)
        task.updated_at = datetime.utcnow()
        self.store_task(task)
        return True

    def clear_all_data(self) -> None:
        """
        Clear all data from the context store. Use with caution!
        """
        with self._get_connection() as conn:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM conversations")
            conn.execute("DELETE FROM tasks")
            conn.execute("DELETE FROM task_results")
            conn.execute("DELETE FROM projects")
            conn.execute("DELETE FROM user_preferences")
            conn.execute("DELETE FROM metrics")
