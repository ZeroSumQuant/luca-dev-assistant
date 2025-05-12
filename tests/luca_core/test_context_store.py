"""Tests for the ContextStore implementation."""

import os
import sys
import tempfile
import uuid
from datetime import datetime

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import pytest

from luca_core.context.store import ContextStore
from luca_core.schemas.context import (Message, MessageRole, MetricRecord,
                                       Project, Task, TaskResult, TaskStatus,
                                       UserPreferences)


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, f"test_context_{uuid.uuid4()}.db")
    yield db_path
    # Clean up the test database after use
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def context_store(temp_db_path):
    """Create a context store instance for testing."""
    store = ContextStore(db_path=temp_db_path)
    yield store


def test_context_store_initialization(context_store, temp_db_path):
    """Test that the context store initializes correctly."""
    assert context_store.db_path == temp_db_path
    assert os.path.exists(temp_db_path)


def test_store_and_retrieve_message(context_store):
    """Test storing and retrieving a message."""
    message_id = str(uuid.uuid4())
    message = Message(
        id=message_id,
        role=MessageRole.USER,
        content="Test message content",
    )

    # Store the message
    stored_id = context_store.store_message(message)
    assert stored_id == message_id

    # Retrieve the message
    retrieved_message = context_store.get_message(message_id)
    assert retrieved_message is not None
    assert retrieved_message.id == message_id
    assert retrieved_message.role == MessageRole.USER
    assert retrieved_message.content == "Test message content"


def test_store_and_retrieve_task(context_store):
    """Test storing and retrieving a task."""
    task_id = str(uuid.uuid4())
    agent_id = "test_agent"
    task = Task(
        id=task_id,
        agent_id=agent_id,
        description="Test task",
        status=TaskStatus.PENDING,
    )

    # Store the task
    stored_id = context_store.store_task(task)
    assert stored_id == task_id

    # Retrieve the task
    retrieved_task = context_store.get_task(task_id)
    assert retrieved_task is not None
    assert retrieved_task.id == task_id
    assert retrieved_task.agent_id == agent_id
    assert retrieved_task.description == "Test task"
    assert retrieved_task.status == TaskStatus.PENDING


def test_store_and_retrieve_task_result(context_store):
    """Test storing and retrieving a task result."""
    task_id = str(uuid.uuid4())
    result = TaskResult(
        task_id=task_id,
        success=True,
        result="Operation completed successfully",
        execution_time_ms=150,
    )

    # Store the task result
    stored_id = context_store.store_task_result(result)
    assert stored_id == task_id

    # Retrieve the task result
    retrieved_result = context_store.get_task_result(task_id)
    assert retrieved_result is not None
    assert retrieved_result.task_id == task_id
    assert retrieved_result.success is True
    assert retrieved_result.result == "Operation completed successfully"
    assert retrieved_result.execution_time_ms == 150


def test_store_and_retrieve_project(context_store):
    """Test storing and retrieving a project."""
    project_id = str(uuid.uuid4())
    project = Project(
        id=project_id,
        name="Test Project",
        description="A test project",
        domain="general",
    )

    # Store the project
    stored_id = context_store.store_project(project)
    assert stored_id == project_id

    # Retrieve the project
    retrieved_project = context_store.get_project(project_id)
    assert retrieved_project is not None
    assert retrieved_project.id == project_id
    assert retrieved_project.name == "Test Project"
    assert retrieved_project.description == "A test project"
    assert retrieved_project.domain == "general"


def test_store_and_retrieve_user_preferences(context_store):
    """Test storing and retrieving user preferences."""
    user_id = "test_user"
    preferences = UserPreferences(
        user_id=user_id,
        learning_mode="guru",
        theme="dark",
        domain_preference="quantitative_finance",
    )

    # Store the preferences
    stored_id = context_store.store_user_preferences(preferences, user_id)
    assert stored_id == user_id

    # Retrieve the preferences
    retrieved_preferences = context_store.get_user_preferences(user_id)
    assert retrieved_preferences is not None
    assert retrieved_preferences.user_id == user_id
    assert retrieved_preferences.learning_mode == "guru"
    assert retrieved_preferences.theme == "dark"
    assert retrieved_preferences.domain_preference == "quantitative_finance"


def test_store_and_retrieve_metric(context_store):
    """Test storing and retrieving a metric record."""
    task_id = str(uuid.uuid4())
    metric = MetricRecord(
        task_id=task_id,
        agent_id="test_agent",
        latency_ms=200,
        error_count=0,
        tokens_used=150,
        completion_status="success",
        domain="general",
        learning_mode="pro",
    )

    # Store the metric
    metric_id = context_store.store_metric(metric)
    assert metric_id is not None

    # Retrieve metrics for the task
    metrics = context_store.get_metrics_for_task(task_id)
    assert len(metrics) == 1
    assert metrics[0].task_id == task_id
    assert metrics[0].agent_id == "test_agent"
    assert metrics[0].latency_ms == 200
    assert metrics[0].error_count == 0
    assert metrics[0].tokens_used == 150
    assert metrics[0].completion_status == "success"
    assert metrics[0].domain == "general"
    assert metrics[0].learning_mode == "pro"
