"""Base interface for context storage.

This module defines the abstract base class for ContextStore implementations,
ensuring consistent behavior across different storage backends.
"""

import abc
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel

from luca_core.schemas import (
    ClarificationRequest,
    Message,
    MetricRecord,
    Project,
    Task,
    TaskResult,
    UserPreferences,
)

T = TypeVar("T", bound=BaseModel)


class BaseContextStore(abc.ABC):
    """Abstract base class for context storage implementations."""

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend.

        This should create any necessary tables or indices.
        """
        pass

    @abc.abstractmethod
    async def store(self, model: BaseModel, namespace: str = "default") -> None:
        """Store a model instance.

        Args:
            model: The model instance to store
            namespace: Optional namespace for organization
        """
        pass

    @abc.abstractmethod
    async def fetch(
        self, model_cls: Type[T], key: str, namespace: str = "default"
    ) -> Optional[T]:
        """Fetch a model instance by key.

        Args:
            model_cls: The model class to fetch
            key: The primary key of the model
            namespace: Optional namespace for organization

        Returns:
            The model instance if found, None otherwise
        """
        pass

    @abc.abstractmethod
    async def update(self, model: BaseModel, namespace: str = "default") -> None:
        """Update an existing model instance.

        Args:
            model: The model instance to update
            namespace: Optional namespace for organization
        """
        pass

    @abc.abstractmethod
    async def delete(
        self, model_cls: Type[BaseModel], key: str, namespace: str = "default"
    ) -> None:
        """Delete a model instance.

        Args:
            model_cls: The model class to delete
            key: The primary key of the model
            namespace: Optional namespace for organization
        """
        pass

    @abc.abstractmethod
    async def list(
        self,
        model_cls: Type[T],
        namespace: str = "default",
        limit: int = 100,
        offset: int = 0,
    ) -> List[T]:
        """List model instances of a specific type.

        Args:
            model_cls: The model class to list
            namespace: Optional namespace for organization
            limit: Maximum number of items to return
            offset: Offset for pagination

        Returns:
            A list of model instances
        """
        pass

    @abc.abstractmethod
    async def query(
        self,
        model_cls: Type[T],
        query: Dict[str, Any],
        namespace: str = "default",
        limit: int = 100,
        offset: int = 0,
    ) -> List[T]:
        """Query model instances based on criteria.

        Args:
            model_cls: The model class to query
            query: A dictionary of key-value pairs to filter by
            namespace: Optional namespace for organization
            limit: Maximum number of items to return
            offset: Offset for pagination

        Returns:
            A list of model instances matching the query
        """
        pass

    # Convenience methods for common operations

    async def get_conversation_history(self, limit: int = 10) -> List[Message]:
        """Get recent conversation history.

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of messages in chronological order
        """
        return await self.list(Message, namespace="conversation", limit=limit)

    async def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks.

        Returns:
            List of pending tasks
        """
        return await self.query(Task, {"status": "pending"}, namespace="tasks")

    async def get_user_preferences(
        self, user_id: str = "default"
    ) -> Optional[UserPreferences]:
        """Get user preferences.

        Args:
            user_id: The ID of the user

        Returns:
            User preferences or None if not found
        """
        return await self.fetch(UserPreferences, user_id, namespace="preferences")

    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID.

        Args:
            project_id: The ID of the project

        Returns:
            Project or None if not found
        """
        return await self.fetch(Project, project_id, namespace="projects")

    async def record_metric(self, metric: MetricRecord) -> None:
        """Record a performance metric.

        Args:
            metric: The metric to record
        """
        await self.store(metric, namespace="metrics")

    async def store_message(self, message: Message) -> None:
        """Store a conversation message.

        Args:
            message: The message to store
        """
        await self.store(message, namespace="conversation")

    async def store_task(self, task: Task) -> None:
        """Store a task.

        Args:
            task: The task to store
        """
        await self.store(task, namespace="tasks")

    async def update_task_status(self, task_id: str, status: str) -> None:
        """Update a task's status.

        Args:
            task_id: The ID of the task
            status: The new status
        """
        task = await self.fetch(Task, task_id, namespace="tasks")
        if task:
            task.status = status
            task.updated_at = datetime.utcnow()
            if status == "completed":
                task.completed_at = datetime.utcnow()
            await self.update(task, namespace="tasks")

    async def store_task_result(self, result: TaskResult) -> None:
        """Store a task result.

        Args:
            result: The task result to store
        """
        await self.store(result, namespace="task_results")
        # Also update the task status
        await self.update_task_status(
            result.task_id, "completed" if result.success else "failed"
        )

    async def request_clarification(self, request: ClarificationRequest) -> None:
        """Store a clarification request.

        Args:
            request: The clarification request to store
        """
        await self.store(request, namespace="clarification_requests")

    async def get_pending_clarification_requests(self) -> List[ClarificationRequest]:
        """Get all pending clarification requests.

        Returns:
            List of unresolved clarification requests
        """
        return await self.query(
            ClarificationRequest,
            {"resolved": False},
            namespace="clarification_requests",
        )
