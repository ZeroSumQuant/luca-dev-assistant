"""Tests for the BaseContextStore abstract class."""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import pytest
from pydantic import BaseModel

from luca_core.context.base_store import BaseContextStore
from luca_core.schemas import (
    ClarificationRequest,
    Message,
    MetricRecord,
    Project,
    Task,
    TaskResult,
    UserPreferences,
)

# Define TypeVar for generic type
T = TypeVar("T", bound=BaseModel)


# Concrete implementation for testing
class MockContextStore(BaseContextStore):
    """Mock implementation of BaseContextStore for testing."""

    def __init__(self):
        self.store_data: Dict[str, Dict[str, Any]] = {}
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the storage backend."""
        self.initialized = True

    async def close(self) -> None:
        """Close the storage backend."""
        self.initialized = False

    async def store(self, model: BaseModel, namespace: str = "default") -> None:
        """Store a model instance."""
        if namespace not in self.store_data:
            self.store_data[namespace] = {}
        # Get the appropriate key for the model
        if hasattr(model, "id"):
            key = model.id
        elif hasattr(model, "user_id"):
            key = model.user_id
        elif hasattr(model, "task_id"):
            key = model.task_id
        else:
            key = str(id(model))
        self.store_data[namespace][key] = model.model_dump()

    async def fetch(
        self, model_cls: Type[T], key: str, namespace: str = "default"
    ) -> Optional[T]:
        """Fetch a model instance by key."""
        if namespace in self.store_data and key in self.store_data[namespace]:
            return model_cls.model_validate(self.store_data[namespace][key])
        return None

    async def update(self, model: BaseModel, namespace: str = "default") -> None:
        """Update an existing model instance."""
        await self.store(model, namespace)

    async def delete(
        self, model_cls: Type[BaseModel], key: str, namespace: str = "default"
    ) -> None:
        """Delete a model instance."""
        if namespace in self.store_data and key in self.store_data[namespace]:
            del self.store_data[namespace][key]

    async def list(
        self,
        model_cls: Type[T],
        namespace: str = "default",
        limit: int = 100,
        offset: int = 0,
    ) -> List[T]:
        """List model instances of a specific type."""
        if namespace not in self.store_data:
            return []
        items = list(self.store_data[namespace].values())[offset : offset + limit]
        return [model_cls.model_validate(item) for item in items]

    async def query(
        self,
        model_cls: Type[T],
        query: Dict[str, Any],
        namespace: str = "default",
        limit: int = 100,
        offset: int = 0,
    ) -> List[T]:
        """Query model instances based on criteria."""
        if namespace not in self.store_data:
            return []
        results = []
        for item in self.store_data[namespace].values():
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                results.append(model_cls.model_validate(item))
        return results[offset : offset + limit]


@pytest.fixture
def store():
    """Create a mock context store instance."""
    return MockContextStore()


@pytest.mark.asyncio
async def test_initialize(store):
    """Test initialize method."""
    assert not store.initialized
    await store.initialize()
    assert store.initialized


@pytest.mark.asyncio
async def test_store_message(store):
    """Test storing a message."""
    await store.initialize()
    message = Message(
        id="msg-1",
        role="user",
        content="Test message",
    )
    await store.store_message(message)

    # Verify the message was stored
    fetched = await store.fetch(Message, "msg-1", namespace="conversation")
    assert fetched is not None
    assert fetched.content == "Test message"


@pytest.mark.asyncio
async def test_get_user_preferences(store):
    """Test getting user preferences."""
    await store.initialize()

    # Store preferences
    prefs = UserPreferences(
        user_id="user-1",
        learning_mode="pro",
        theme="dark",
        domain_preference="general",
    )
    await store.store(prefs, namespace="preferences")

    # Get preferences
    retrieved = await store.get_user_preferences("user-1")
    assert retrieved is not None
    assert retrieved.learning_mode == "pro"


@pytest.mark.asyncio
async def test_get_user_preferences_not_found(store):
    """Test getting non-existent user preferences."""
    await store.initialize()
    prefs = await store.get_user_preferences("nonexistent")
    assert prefs is None


@pytest.mark.asyncio
async def test_get_project(store):
    """Test getting a project."""
    await store.initialize()

    # Store project
    project = Project(
        id="proj-1",
        name="Test Project",
        description="A test project",
        domain="general",
    )
    await store.store(project, namespace="projects")

    # Get project
    retrieved = await store.get_project("proj-1")
    assert retrieved is not None
    assert retrieved.name == "Test Project"


@pytest.mark.asyncio
async def test_get_project_not_found(store):
    """Test getting a non-existent project."""
    await store.initialize()
    project = await store.get_project("nonexistent")
    assert project is None


@pytest.mark.asyncio
async def test_record_metric(store):
    """Test recording a metric."""
    await store.initialize()

    metric = MetricRecord(
        task_id="task-1",
        agent_id="agent-1",
        latency_ms=100,
        error_count=0,
        tokens_used=50,
        completion_status="success",
        domain="general",
        learning_mode="pro",
    )
    await store.record_metric(metric)

    # Verify metric was stored
    stored = await store.fetch(MetricRecord, metric.task_id, namespace="metrics")
    assert stored is not None
    assert stored.latency_ms == 100


@pytest.mark.asyncio
async def test_store_task(store):
    """Test storing a task."""
    await store.initialize()

    task = Task(
        id="task-1",
        agent_id="agent-1",
        description="Test task",
        status="pending",
    )
    await store.store_task(task)

    # Verify task was stored
    stored = await store.fetch(Task, "task-1", namespace="tasks")
    assert stored is not None
    assert stored.description == "Test task"


@pytest.mark.asyncio
async def test_update_task_status(store):
    """Test updating task status."""
    await store.initialize()

    # Store initial task
    task = Task(
        id="task-1",
        agent_id="agent-1",
        description="Test task",
        status="pending",
    )
    await store.store_task(task)

    # Update status
    await store.update_task_status("task-1", "completed")

    # Verify status was updated
    updated = await store.fetch(Task, "task-1", namespace="tasks")
    assert updated is not None
    assert updated.status == "completed"
    assert updated.completed_at is not None


@pytest.mark.asyncio
async def test_update_task_status_not_found(store):
    """Test updating status of non-existent task."""
    await store.initialize()
    # This should not raise an error, just do nothing
    await store.update_task_status("nonexistent", "completed")


@pytest.mark.asyncio
async def test_store_task_result(store):
    """Test storing a task result."""
    await store.initialize()

    # Store initial task
    task = Task(
        id="task-1",
        agent_id="agent-1",
        description="Test task",
        status="pending",
    )
    await store.store_task(task)

    # Store task result
    result = TaskResult(
        task_id="task-1",
        success=True,
        result={"data": "test"},
        execution_time_ms=100,
    )
    await store.store_task_result(result)

    # Verify result was stored
    stored = await store.fetch(TaskResult, "task-1", namespace="task_results")
    assert stored is not None
    assert stored.success is True

    # Verify task status was updated
    updated_task = await store.fetch(Task, "task-1", namespace="tasks")
    assert updated_task is not None
    assert updated_task.status == "completed"


@pytest.mark.asyncio
async def test_store_task_result_failure(store):
    """Test storing a failed task result."""
    await store.initialize()

    # Store initial task
    task = Task(
        id="task-1",
        agent_id="agent-1",
        description="Test task",
        status="pending",
    )
    await store.store_task(task)

    # Store failed task result
    result = TaskResult(
        task_id="task-1",
        success=False,
        result=None,
        error_message="Test error",
        execution_time_ms=100,
    )
    await store.store_task_result(result)

    # Verify task status was updated to failed
    updated_task = await store.fetch(Task, "task-1", namespace="tasks")
    assert updated_task is not None
    assert updated_task.status == "failed"


@pytest.mark.asyncio
async def test_request_clarification(store):
    """Test storing a clarification request."""
    await store.initialize()

    request = ClarificationRequest(
        id="req-1",
        task_id="task-1",
        agent_id="agent-1",
        question="What do you mean?",
    )
    await store.request_clarification(request)

    # Verify request was stored
    stored = await store.fetch(
        ClarificationRequest, "req-1", namespace="clarification_requests"
    )
    assert stored is not None
    assert stored.question == "What do you mean?"


@pytest.mark.asyncio
async def test_get_pending_clarification_requests(store):
    """Test getting pending clarification requests."""
    await store.initialize()

    # Store multiple clarification requests
    req1 = ClarificationRequest(
        id="req-1",
        task_id="task-1",
        agent_id="agent-1",
        question="Question 1",
        resolved=False,
    )
    req2 = ClarificationRequest(
        id="req-2",
        task_id="task-2",
        agent_id="agent-1",
        question="Question 2",
        resolved=True,
    )
    req3 = ClarificationRequest(
        id="req-3",
        task_id="task-3",
        agent_id="agent-1",
        question="Question 3",
        resolved=False,
    )

    await store.request_clarification(req1)
    await store.request_clarification(req2)
    await store.request_clarification(req3)

    # Get pending requests
    pending = await store.get_pending_clarification_requests()
    assert len(pending) == 2
    assert all(not req.resolved for req in pending)


@pytest.mark.asyncio
async def test_get_conversation_history(store):
    """Test getting conversation history."""
    await store.initialize()

    # Store messages in conversation namespace
    for i in range(5):
        message = Message(
            id=f"msg-{i}",
            role="user",
            content=f"Message {i}",
        )
        await store.store(message, namespace="conversation")

    # Get conversation history
    history = await store.get_conversation_history(limit=3)
    assert len(history) == 3


@pytest.mark.asyncio
async def test_get_pending_tasks(store):
    """Test getting pending tasks."""
    await store.initialize()

    # Store tasks with different statuses
    pending_task = Task(
        id="task-1",
        agent_id="agent-1",
        description="Pending task",
        status="pending",
    )
    completed_task = Task(
        id="task-2",
        agent_id="agent-1",
        description="Completed task",
        status="completed",
    )

    await store.store(pending_task, namespace="tasks")
    await store.store(completed_task, namespace="tasks")

    # Get pending tasks
    pending = await store.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].status == "pending"


@pytest.mark.asyncio
async def test_abstract_methods_require_implementation():
    """Test that abstract methods require implementation."""
    from abc import ABC

    class IncompleteStore(BaseContextStore):
        pass

    # Should not be able to instantiate an incomplete implementation
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        store = IncompleteStore()


@pytest.mark.asyncio
async def test_abstract_method_coverage():
    """Test abstract methods to cover pass statements."""

    # Create a minimal implementation that calls super() to execute the pass statements
    class CoverageStore(BaseContextStore):
        """A minimal implementation for coverage testing."""

        async def initialize(self):
            # Call the parent method to execute the pass statement
            return await super().initialize()

        async def store(self, model, namespace="default"):
            return await super().store(model, namespace)

        async def fetch(self, model_cls, key, namespace="default"):
            return await super().fetch(model_cls, key, namespace)

        async def update(self, model, namespace="default"):
            return await super().update(model, namespace)

        async def delete(self, model_cls, key, namespace="default"):
            return await super().delete(model_cls, key, namespace)

        async def list(self, model_cls, namespace="default", limit=100, offset=0):
            return await super().list(model_cls, namespace, limit, offset)

        async def query(
            self, model_cls, query, namespace="default", limit=100, offset=0
        ):
            return await super().query(model_cls, query, namespace, limit, offset)

    # Create instance and call methods to execute the pass statements
    store = CoverageStore()

    # Each of these calls will execute the pass statement in the base class
    await store.initialize()
    await store.store(None)
    await store.fetch(None, "")
    await store.update(None)
    await store.delete(None, "")
    await store.list(None)
    await store.query(None, {})
