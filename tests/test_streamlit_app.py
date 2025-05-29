"""Tests for Streamlit app components."""

import sys
import unittest.mock as mock

import pytest


def test_main_modern_import():
    """Test that main_modern.py can be imported without errors."""
    # Create a comprehensive mock for streamlit
    mock_st = mock.MagicMock()
    mock_st.set_page_config = mock.MagicMock()
    mock_st.markdown = mock.MagicMock()
    mock_st.columns = mock.MagicMock(
        return_value=[mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]
    )
    mock_st.container = mock.MagicMock()
    mock_st.form = mock.MagicMock()
    mock_st.text_area = mock.MagicMock(return_value="")
    mock_st.form_submit_button = mock.MagicMock(return_value=False)
    mock_st.spinner = mock.MagicMock()
    mock_st.rerun = mock.MagicMock()
    mock_st.session_state = {}
    mock_st.sidebar = mock.MagicMock()
    mock_st.sidebar.__enter__ = mock.Mock(return_value=mock_st.sidebar)
    mock_st.sidebar.__exit__ = mock.Mock(return_value=None)
    mock_st.page_link = mock.MagicMock()
    mock_st.divider = mock.MagicMock()
    mock_st.selectbox = mock.MagicMock(return_value="Quantitative Trading")

    # Mock streamlit.components.v1
    mock_components = mock.MagicMock()
    mock_components.html = mock.MagicMock()

    # Set up the module mocks
    sys.modules["streamlit"] = mock_st
    sys.modules["streamlit.components"] = mock.MagicMock()
    sys.modules["streamlit.components.v1"] = mock_components

    try:
        # Clear any cached import
        if "app.main_modern" in sys.modules:
            del sys.modules["app.main_modern"]

        import app.main_modern

        # Should have been imported successfully
        assert app.main_modern is not None
    except ImportError as e:
        pytest.fail(f"Failed to import main_modern: {e}")
    finally:
        # Clean up
        if "app.main_modern" in sys.modules:
            del sys.modules["app.main_modern"]
        if "streamlit" in sys.modules:
            del sys.modules["streamlit"]
        if "streamlit.components" in sys.modules:
            del sys.modules["streamlit.components"]
        if "streamlit.components.v1" in sys.modules:
            del sys.modules["streamlit.components.v1"]


def test_agent_manager_import():
    """Test that agent manager page can be imported without errors."""
    # Mock streamlit and its components before import
    mock_st = mock.MagicMock()
    mock_components = mock.MagicMock()
    mock_components.v1 = mock.MagicMock()
    mock_components.v1.html = mock.MagicMock()

    sys.modules["streamlit"] = mock_st
    sys.modules["streamlit.components"] = mock_components
    sys.modules["streamlit.components.v1"] = mock_components.v1

    try:
        # Clear any cached import
        if "app.pages.agent_manager" in sys.modules:
            del sys.modules["app.pages.agent_manager"]

        import app.pages.agent_manager

        # Should have been imported successfully
        assert app.pages.agent_manager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import agent manager: {e}")
    finally:
        # Clean up
        for module in [
            "app.pages.agent_manager",
            "streamlit",
            "streamlit.components",
            "streamlit.components.v1",
        ]:
            if module in sys.modules:
                del sys.modules[module]


def test_agent_config():
    """Test that the agent configuration is valid."""
    # Mock streamlit and its components before import
    mock_st = mock.MagicMock()
    mock_components = mock.MagicMock()
    mock_components.v1 = mock.MagicMock()
    mock_components.v1.html = mock.MagicMock()

    sys.modules["streamlit"] = mock_st
    sys.modules["streamlit.components"] = mock_components
    sys.modules["streamlit.components.v1"] = mock_components.v1

    from app.pages.agent_manager import AGENT_CONFIG

    # Verify structure
    assert isinstance(AGENT_CONFIG, dict)
    assert "luca" in AGENT_CONFIG

    # Verify each agent has required fields
    for agent_id, agent_info in AGENT_CONFIG.items():
        assert "name" in agent_info
        assert "role" in agent_info
        assert "description" in agent_info
        assert "color" in agent_info


def test_agent_manager_imports():
    """Test that agent manager can import required modules."""
    # Mock streamlit and its components before import
    mock_st = mock.MagicMock()
    mock_components = mock.MagicMock()
    mock_components.v1 = mock.MagicMock()
    mock_components.v1.html = mock.MagicMock()

    sys.modules["streamlit"] = mock_st
    sys.modules["streamlit.components"] = mock_components
    sys.modules["streamlit.components.v1"] = mock_components.v1

    # Clear any cached import
    if "app.pages.agent_manager" in sys.modules:
        del sys.modules["app.pages.agent_manager"]

    # This should not raise any exceptions
    import app.pages.agent_manager

    # Verify the module has the expected structure
    assert hasattr(app.pages.agent_manager, "AGENT_CONFIG")
    assert hasattr(app.pages.agent_manager, "html_content")
