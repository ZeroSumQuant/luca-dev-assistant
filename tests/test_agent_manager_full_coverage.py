"""Complete test coverage for app/pages/agent_manager.py."""

import json
import unittest.mock as mock

import pytest


class TestAgentManagerFullCoverage:
    """Test for full coverage of agent_manager.py."""

    @mock.patch("streamlit.set_page_config")
    @mock.patch("streamlit.session_state", new_callable=lambda: mock.MagicMock())
    def test_module_initialization(self, mock_session_state, mock_set_page_config):
        """Test module level initialization."""
        # Set up session state to not have agent_config initially
        mock_session_state.__contains__.return_value = False
        mock_session_state.__getitem__.side_effect = KeyError

        # Import the module to trigger initialization
        import importlib
        import sys

        if "app.pages.agent_manager" in sys.modules:
            del sys.modules["app.pages.agent_manager"]

        with mock.patch("streamlit.markdown"):
            import app.pages.agent_manager

        # Verify set_page_config was called
        mock_set_page_config.assert_called_once()

        # Verify agent_config was initialized
        assert mock_session_state.__setitem__.called
        mock_session_state.__setitem__.assert_any_call("agent_config", mock.ANY)

    @mock.patch("app.pages.agent_manager.st")
    @mock.patch("graphviz.Digraph")
    def test_create_agent_tree_function(self, mock_digraph, mock_st):
        """Test create_agent_tree function separately."""
        # Import without triggering module initialization
        import app.pages.agent_manager

        # Mock the session state
        agent_config = {
            "luca": {
                "name": "Luca",
                "model": "gpt-4",
                "color": "#1E88E5",
            },
            "coder": {
                "name": "Coder",
                "model": "gpt-4",
                "color": "#4CAF50",
            },
        }

        custom_agents = [
            {"name": "CustomAgent", "description": "Test agent", "domain": "testing"}
        ]

        mock_st.session_state.agent_config = agent_config
        mock_st.session_state.custom_agents = custom_agents

        # Mock the Digraph object
        mock_dot = mock.Mock()
        mock_digraph.return_value = mock_dot

        # Call the function
        result = app.pages.agent_manager.create_agent_tree()

        # Verify calls
        mock_digraph.assert_called_once_with(comment="Agent Tree")
        mock_dot.attr.assert_called()
        mock_dot.node.assert_called()
        mock_dot.edge.assert_called()
        assert result == mock_dot

    @mock.patch("app.pages.agent_manager.st")
    def test_main_function_complete(self, mock_st):
        """Test the main function with all branches."""
        import app.pages.agent_manager

        # Setup mocks
        mock_tabs = [mock.Mock(), mock.Mock(), mock.Mock()]
        for i, tab in enumerate(mock_tabs):
            tab.__enter__ = mock.Mock(return_value=tab)
            tab.__exit__ = mock.Mock(return_value=None)

        mock_st.tabs.return_value = mock_tabs

        # Mock session state
        agent_config = {
            "luca": {"name": "Luca", "model": "gpt-4", "color": "#1E88E5"},
            "coder": {"name": "Coder", "model": "gpt-4", "color": "#4CAF50"},
        }

        custom_agents = []

        # Create a more comprehensive mock for session state
        session_state_dict = {
            "agent_config": agent_config,
            "custom_agents": custom_agents,
        }

        class MockSessionState:
            def __init__(self, data):
                self._data = data

            def __getattr__(self, name):
                if name in self._data:
                    return self._data[name]
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{name}'"
                )

            def __setattr__(self, name, value):
                if name.startswith("_"):
                    object.__setattr__(self, name, value)
                else:
                    self._data[name] = value

            def __setitem__(self, key, value):
                self._data[key] = value

            def __getitem__(self, key):
                return self._data[key]

            def __contains__(self, key):
                return key in self._data

            def get(self, key, default=None):
                return self._data.get(key, default)

        mock_st.session_state = MockSessionState(session_state_dict)

        # Mock columns and selectbox
        mock_cols = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_st.columns.return_value = mock_cols
        mock_st.selectbox.return_value = "luca"

        # Mock form
        mock_form = mock.Mock()
        mock_form.__enter__ = mock.Mock(return_value=mock_form)
        mock_form.__exit__ = mock.Mock(return_value=None)
        mock_st.form.return_value = mock_form

        # Setup form inputs
        mock_st.text_input.side_effect = [
            "NewAgent",
            "Test description",
            "python test.py",
        ]
        mock_st.text_area.return_value = "Test agent description"
        mock_st.multiselect.return_value = ["gpt-4"]
        mock_st.form_submit_button.return_value = True

        # Mock create_agent_tree to test error path
        with mock.patch(
            "app.pages.agent_manager.create_agent_tree"
        ) as mock_create_tree:
            # First call succeeds, second call fails
            mock_create_tree.side_effect = [
                mock.Mock(source="graph TD"),
                Exception("Tree error"),
            ]

            # Run main
            app.pages.agent_manager.main()

            # Run again to trigger error path
            app.pages.agent_manager.main()

        # Verify markdown headers were called
        mock_st.markdown.assert_any_call("# 🌳 Agent Manager")

        # Verify error was shown on second run
        mock_st.error.assert_called()

        # Verify fallback tree was shown
        mock_st.markdown.assert_any_call("🧠 Luca (Manager)")

    @mock.patch("app.pages.agent_manager.st")
    def test_agent_status_tab_coverage(self, mock_st):
        """Test agent status tab with custom agents."""
        import app.pages.agent_manager

        # Setup
        mock_tabs = [mock.Mock(), mock.Mock(), mock.Mock()]
        for tab in mock_tabs:
            tab.__enter__ = mock.Mock(return_value=tab)
            tab.__exit__ = mock.Mock(return_value=None)

        mock_st.tabs.return_value = mock_tabs

        # Mock session state with custom agents
        custom_agents = [
            {
                "name": "TestAgent",
                "description": "Test agent",
                "domain": "testing",
                "created_at": "2025-05-19T12:00:00",
            }
        ]

        agent_config = app.pages.agent_manager.DEFAULT_AGENT_CONFIG.copy()

        mock_st.session_state.agent_config = agent_config
        mock_st.session_state.custom_agents = custom_agents

        # Mock other UI elements
        mock_st.columns.return_value = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_st.selectbox.return_value = None

        # Run main
        app.pages.agent_manager.main()

        # Verify custom agents were displayed
        mock_st.json.assert_called()

    @mock.patch("app.pages.agent_manager.st")
    def test_reset_to_defaults(self, mock_st):
        """Test reset to defaults functionality."""
        import app.pages.agent_manager

        # Setup
        mock_tabs = [mock.Mock(), mock.Mock(), mock.Mock()]
        for tab in mock_tabs:
            tab.__enter__ = mock.Mock(return_value=tab)
            tab.__exit__ = mock.Mock(return_value=None)

        mock_st.tabs.return_value = mock_tabs

        # Mock session state
        mock_st.session_state.agent_config = {"modified": "config"}
        mock_st.session_state.custom_agents = []

        # Mock button to trigger reset
        mock_st.button.return_value = True

        # Mock other UI elements
        mock_st.columns.return_value = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_st.selectbox.return_value = None

        # Run main
        app.pages.agent_manager.main()

        # Verify reset happened
        assert mock_st.session_state.agent_config != {"modified": "config"}
        mock_st.success.assert_called_with("Reset to default agent configuration")
