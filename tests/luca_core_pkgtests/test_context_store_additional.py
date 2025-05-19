"""Additional tests for ContextStore to reach 95% coverage."""

import os
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import pytest

from luca_core.context.store import ContextStore
from luca_core.schemas.context import (
    Conversation,
    Message,
    MessageRole,
    MetricRecord,
    Project,
    Task,
    TaskResult,
    TaskStatus,
    UserPreferences,
)


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


def test_store_and_retrieve_conversation(context_store):
    """Test storing and retrieving a conversation."""
    conversation_id = str(uuid.uuid4())
    project_id = str(uuid.uuid4())
    conversation = Conversation(
        id=conversation_id,
        title="Test Conversation",
        project_id=project_id,
    )

    # Store the conversation
    stored_id = context_store.store_conversation(conversation)
    assert stored_id == conversation_id

    # Retrieve the conversation
    retrieved_conversation = context_store.get_conversation(conversation_id)
    assert retrieved_conversation is not None
    assert retrieved_conversation.id == conversation_id
    assert retrieved_conversation.project_id == project_id
    assert retrieved_conversation.title == "Test Conversation"


def test_get_nonexistent_conversation(context_store):
    """Test retrieving a non-existent conversation."""
    retrieved_conversation = context_store.get_conversation("nonexistent")
    assert retrieved_conversation is None


def test_store_and_retrieve_message_with_conversation(context_store):
    """Test storing and retrieving a message with conversation ID."""
    message_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())

    # Create a conversation first
    conversation = Conversation(
        id=conversation_id,
        title="Test Conversation",
    )
    context_store.store_conversation(conversation)

    # Store a message with conversation ID
    message = Message(
        id=message_id,
        role=MessageRole.USER,
        content="Test message content",
    )
    stored_id = context_store.store_message(message, conversation_id=conversation_id)
    assert stored_id == message_id

    # Get the conversation's messages
    messages = context_store.get_conversation_messages(conversation_id)
    assert len(messages) == 1
    assert messages[0].id == message_id
    assert messages[0].content == "Test message content"


def test_get_conversation_messages_empty(context_store):
    """Test getting messages for a conversation with no messages."""
    conversation_id = str(uuid.uuid4())
    messages = context_store.get_conversation_messages(conversation_id)
    assert len(messages) == 0


def test_get_project_conversations(context_store):
    """Test getting conversations for a project."""
    project_id = str(uuid.uuid4())

    # Store multiple conversations for the same project
    for i in range(3):
        conversation = Conversation(
            id=str(uuid.uuid4()),
            title=f"Test Conversation {i}",
            project_id=project_id,
        )
        context_store.store_conversation(conversation)

    # Store a conversation for a different project
    other_conversation = Conversation(
        id=str(uuid.uuid4()),
        title="Other Project Conversation",
        project_id=str(uuid.uuid4()),
    )
    context_store.store_conversation(other_conversation)

    # Get conversations for the project
    project_conversations = context_store.get_project_conversations(project_id)
    assert len(project_conversations) == 3

    # Verify all conversations belong to the correct project
    for conv in project_conversations:
        assert conv.project_id == project_id


def test_store_task_with_conversation(context_store):
    """Test storing a task with conversation ID."""
    task_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())

    task = Task(
        id=task_id,
        agent_id="test_agent",
        description="Test task",
        status=TaskStatus.PENDING,
    )

    # Store the task with conversation ID
    stored_id = context_store.store_task(task, conversation_id=conversation_id)
    assert stored_id == task_id

    # Retrieve the task
    retrieved_task = context_store.get_task(task_id)
    assert retrieved_task is not None
    assert retrieved_task.id == task_id


def test_get_active_tasks(context_store):
    """Test getting active tasks."""
    # Store multiple tasks with different statuses
    active_statuses = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
    inactive_statuses = [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED]

    active_count = 0
    for status in active_statuses:
        task = Task(
            id=str(uuid.uuid4()),
            agent_id="test_agent",
            description=f"Task with status {status}",
            status=status,
        )
        context_store.store_task(task)
        active_count += 1

    for status in inactive_statuses:
        task = Task(
            id=str(uuid.uuid4()),
            agent_id="test_agent",
            description=f"Task with status {status}",
            status=status,
        )
        context_store.store_task(task)

    # Get active tasks
    active_tasks = context_store.get_active_tasks()
    assert len(active_tasks) == active_count

    # Verify all returned tasks are active
    for task in active_tasks:
        assert task.status in active_statuses


def test_update_task_status(context_store):
    """Test updating task status."""
    task_id = str(uuid.uuid4())

    # Create and store a task
    task = Task(
        id=task_id,
        agent_id="test_agent",
        description="Test task",
        status=TaskStatus.PENDING,
    )
    context_store.store_task(task)

    # Update the task status
    success = context_store.update_task_status(task_id, TaskStatus.IN_PROGRESS.value)
    assert success

    # Verify the status was updated
    updated_task = context_store.get_task(task_id)
    assert updated_task is not None
    assert updated_task.status == TaskStatus.IN_PROGRESS


def test_update_task_status_nonexistent(context_store):
    """Test updating status of non-existent task."""
    success = context_store.update_task_status(
        "nonexistent", TaskStatus.COMPLETED.value
    )
    assert not success


def test_get_user_preferences_returns_default(context_store):
    """Test that get_user_preferences returns default for nonexistent user."""
    # The current implementation returns a default UserPreferences object
    prefs = context_store.get_user_preferences("nonexistent")
    assert isinstance(prefs, UserPreferences)
    assert prefs.user_id == "nonexistent"  # Should use the provided user_id


def test_clear_all_data(context_store):
    """Test clearing all data."""
    # Store some data
    message = Message(
        id=str(uuid.uuid4()),
        role=MessageRole.USER,
        content="Test message",
    )
    context_store.store_message(message)

    task = Task(
        id=str(uuid.uuid4()),
        agent_id="test_agent",
        description="Test task",
    )
    context_store.store_task(task)

    # Clear all data
    context_store.clear_all_data()

    # Verify data is cleared
    retrieved_message = context_store.get_message(message.id)
    assert retrieved_message is None

    retrieved_task = context_store.get_task(task.id)
    assert retrieved_task is None


def test_get_metrics_for_task(context_store):
    """Test getting metrics for a specific task."""
    task_id = str(uuid.uuid4())

    # Store multiple metrics for the same task
    for i in range(3):
        metric = MetricRecord(
            task_id=task_id,
            agent_id=f"agent_{i}",
            latency_ms=100 + i * 10,
            error_count=0,
            tokens_used=50 + i * 5,
            domain="general",
            learning_mode="pro",
            completion_status="success",
        )
        context_store.store_metric(metric)

    # Store a metric for a different task
    other_metric = MetricRecord(
        task_id=str(uuid.uuid4()),
        agent_id="other_agent",
        latency_ms=200,
        error_count=1,
        tokens_used=100,
        domain="general",
        learning_mode="pro",
        completion_status="failure",
    )
    context_store.store_metric(other_metric)

    # Get metrics for the specific task
    task_metrics = context_store.get_metrics_for_task(task_id)
    assert len(task_metrics) == 3

    # Verify all metrics belong to the correct task
    for metric in task_metrics:
        assert metric.task_id == task_id


def test_get_metrics_for_nonexistent_task(context_store):
    """Test getting metrics for a task with no metrics."""
    metrics = context_store.get_metrics_for_task("nonexistent")
    assert len(metrics) == 0


def test_message_retrieval_none(context_store):
    """Test retrieving a non-existent message."""
    retrieved_message = context_store.get_message("nonexistent")
    assert retrieved_message is None


def test_store_project_and_retrieve(context_store):
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


def test_get_project_nonexistent(context_store):
    """Test retrieving a non-existent project."""
    retrieved_project = context_store.get_project("nonexistent")
    assert retrieved_project is None


def test_store_user_preferences_and_retrieve(context_store):
    """Test storing and retrieving user preferences."""
    user_id = str(uuid.uuid4())
    preferences = UserPreferences(
        user_id=user_id,
        learning_mode="guru",
        theme="dark",
        domain_preference="quantitative_finance",
    )

    # Store the preferences
    context_store.store_user_preferences(preferences, user_id)

    # Retrieve the preferences
    retrieved_preferences = context_store.get_user_preferences(user_id)
    assert retrieved_preferences is not None
    assert retrieved_preferences.user_id == user_id
    assert retrieved_preferences.learning_mode == "guru"
    assert retrieved_preferences.theme == "dark"
    assert retrieved_preferences.domain_preference == "quantitative_finance"


def test_get_user_preferences_handles_error(context_store):
    """Test that get_user_preferences handles nonexistent user correctly."""
    # The implementation returns a default UserPreferences with the given user_id
    prefs = context_store.get_user_preferences("nonexistent")
    assert isinstance(prefs, UserPreferences)
    assert prefs.user_id == "nonexistent"


def test_task_retrieval_none(context_store):
    """Test retrieving a non-existent task."""
    retrieved_task = context_store.get_task("nonexistent")
    assert retrieved_task is None


def test_task_result_retrieval_none(context_store):
    """Test retrieving a non-existent task result."""
    retrieved_result = context_store.get_task_result("nonexistent")
    assert retrieved_result is None


def test_store_and_retrieve_task_result(context_store):
    """Test storing and retrieving a task result."""
    task_id = str(uuid.uuid4())

    # Store a task result
    result = TaskResult(
        task_id=task_id,
        success=True,
        result={"data": "test result"},
        execution_time_ms=150,
    )
    stored_id = context_store.store_task_result(result)
    assert stored_id == task_id

    # Retrieve the task result
    retrieved_result = context_store.get_task_result(task_id)
    assert retrieved_result is not None
    assert retrieved_result.task_id == task_id
    assert retrieved_result.success is True
    assert retrieved_result.result == {"data": "test result"}
    assert retrieved_result.execution_time_ms == 150


def test_message_retrieval_existing(context_store):
    """Test retrieving an existing message."""
    message_id = str(uuid.uuid4())

    # Store a message (without conversation_id)
    message = Message(
        id=message_id,
        role=MessageRole.ASSISTANT,
        content="Test response",
    )
    context_store.store_message(message)

    # Retrieve the message
    retrieved_message = context_store.get_message(message_id)
    assert retrieved_message is not None
    assert retrieved_message.id == message_id
    assert retrieved_message.role == MessageRole.ASSISTANT
    assert retrieved_message.content == "Test response"
