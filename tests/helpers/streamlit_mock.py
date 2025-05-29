"""Streamlit mocking utilities for tests."""

import sys
from unittest.mock import MagicMock, patch


class MockSessionState:
    """Mock Streamlit session state."""

    def __init__(self):
        self._state = {}

    def __getattr__(self, name):
        return self._state.get(name, None)

    def __setattr__(self, name, value):
        if name == "_state":
            super().__setattr__(name, value)
        else:
            self._state[name] = value

    def __contains__(self, name):
        return name in self._state

    def get(self, name, default=None):
        return self._state.get(name, default)


def create_streamlit_mock():
    """Create a complete Streamlit mock."""
    mock = MagicMock()

    # Mock session state
    mock.session_state = MockSessionState()

    # Mock common Streamlit functions
    mock.set_page_config = MagicMock()
    mock.markdown = MagicMock()
    mock.title = MagicMock()
    mock.header = MagicMock()
    mock.subheader = MagicMock()
    mock.write = MagicMock()
    mock.button = MagicMock(return_value=False)
    mock.text_input = MagicMock(return_value="")
    mock.text_area = MagicMock(return_value="")
    mock.selectbox = MagicMock(return_value=None)
    mock.checkbox = MagicMock(return_value=False)
    mock.slider = MagicMock(return_value=0)
    mock.columns = MagicMock(return_value=[mock, mock, mock])
    mock.tabs = MagicMock(return_value=[mock, mock])
    mock.container = MagicMock(return_value=mock)
    mock.empty = MagicMock(return_value=mock)
    mock.sidebar = mock
    mock.components = MagicMock()
    mock.components.v1 = MagicMock()
    mock.components.v1.html = MagicMock()

    # Mock context managers
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=None)

    # Make columns and tabs return context managers
    def mock_columns(*args):
        if args:
            # Handle both integer and list inputs
            if isinstance(args[0], int):
                return [mock] * args[0]
            elif isinstance(args[0], list):
                return [mock] * len(args[0])
        return [mock] * 2

    def mock_tabs(tabs):
        return [mock] * len(tabs)

    mock.columns.side_effect = mock_columns
    mock.tabs.side_effect = mock_tabs

    return mock


def patch_streamlit():
    """Create a patch for Streamlit module."""
    mock = create_streamlit_mock()
    return patch.dict(sys.modules, {"streamlit": mock})


def setup_streamlit_test():
    """Setup test environment with Streamlit mocked."""
    mock = create_streamlit_mock()
    sys.modules["streamlit"] = mock
    return mock
