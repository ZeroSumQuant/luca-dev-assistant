"""Tests for Streamlit components."""

import os
import sys

import pytest

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))


def test_main_app_imports():
    """Test that main app can be imported without errors."""
    try:
        import app.main  # noqa: F401

        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import main app: {e}")


def test_agent_manager_imports():
    """Test that agent manager page can be imported without errors."""
    try:
        import app.pages.agent_manager  # noqa: F401

        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import agent manager: {e}")


def test_default_agent_config():
    """Test that the default agent configuration is valid."""
    from app.pages.agent_manager import DEFAULT_AGENT_CONFIG

    # Verify structure
    assert isinstance(DEFAULT_AGENT_CONFIG, dict)
    assert "luca" in DEFAULT_AGENT_CONFIG

    # Verify each agent has required fields
    for agent_id, agent_info in DEFAULT_AGENT_CONFIG.items():
        assert "name" in agent_info
        assert "role" in agent_info
        assert "description" in agent_info
        assert "model" in agent_info
        assert "available_models" in agent_info
        assert "status" in agent_info
        assert "color" in agent_info

        # Verify model is in available_models
        assert agent_info["model"] in agent_info["available_models"]


def test_agent_tree_creation():
    """Test that agent tree can be created without errors."""
    from app.pages.agent_manager import DEFAULT_AGENT_CONFIG, create_agent_tree

    # Mock session state
    class MockSessionState:
        agent_config = DEFAULT_AGENT_CONFIG.copy()

    # Create a mock st module with session_state
    sys.modules["streamlit"].session_state = MockSessionState()

    try:
        dot = create_agent_tree()
        assert dot is not None
        # Verify it's a graphviz.Digraph object
        assert hasattr(dot, "source")
    except Exception as e:
        pytest.fail(f"Failed to create agent tree: {e}")
