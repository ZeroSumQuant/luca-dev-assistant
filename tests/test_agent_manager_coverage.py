"""Test coverage for app/pages/agent_manager.py."""

import json
import unittest.mock as mock

import pytest
import streamlit as st

from app.pages.agent_manager import create_agent_tree, main


class TestAgentManagerCoverage:
    """Test coverage for agent_manager.py to reach 95%."""

    @mock.patch("app.pages.agent_manager.st")
    @pytest.mark.skip_ci
    @pytest.mark.issue_82
    def test_main_happy_path(self, mock_st):
        """Test the main function with normal execution."""
        # Mock streamlit components
        mock_tabs = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_st.tabs.return_value = mock_tabs

        # Mock selectbox to return a valid agent key
        mock_st.selectbox.return_value = "luca"

        # Create column mocks as context managers
        def create_mock_column():
            col = mock.Mock()
            col.__enter__ = mock.Mock(return_value=col)
            col.__exit__ = mock.Mock(return_value=None)
            return col

        # Mock columns to return correct number of columns for each call
        mock_st.columns.side_effect = [
            [
                create_mock_column(),
                create_mock_column(),
                create_mock_column(),
            ],  # Line 123: 3 columns
            [create_mock_column(), create_mock_column()],  # Line 136: 2 columns
            [
                create_mock_column(),
                create_mock_column(),
                create_mock_column(),
            ],  # Line 170: 3 columns
            [
                create_mock_column(),
                create_mock_column(),
            ],  # Line 186: 2 columns (agent 1)
            [
                create_mock_column(),
                create_mock_column(),
            ],  # Line 186: 2 columns (agent 2)
            [
                create_mock_column(),
                create_mock_column(),
            ],  # Line 186: 2 columns (agent 3)
            [
                create_mock_column(),
                create_mock_column(),
            ],  # Line 186: 2 columns (agent 4)
            [
                create_mock_column(),
                create_mock_column(),
            ],  # Line 186: 2 columns (agent 5)
            [
                create_mock_column(),
                create_mock_column(),
                create_mock_column(),
            ],  # Line 196: 3 columns
        ]

        # Mock button to return False (no buttons clicked)
        mock_st.button.return_value = False

        # Setup session state with required attributes
        from app.pages.agent_manager import DEFAULT_AGENT_CONFIG

        session_state_dict = {
            "custom_agents": [],
            "agent_config": DEFAULT_AGENT_CONFIG.copy(),
        }

        class MockSessionState(dict):
            def __getattr__(self, name):
                return self[name]

            def __setattr__(self, name, value):
                self[name] = value

            def __contains__(self, name):
                return dict.__contains__(self, name)

        mock_st.session_state = MockSessionState(session_state_dict)

        # Tab contexts
        mock_tabs[0].__enter__ = mock.Mock(return_value=mock_tabs[0])
        mock_tabs[0].__exit__ = mock.Mock(return_value=None)
        mock_tabs[1].__enter__ = mock.Mock(return_value=mock_tabs[1])
        mock_tabs[1].__exit__ = mock.Mock(return_value=None)
        mock_tabs[2].__enter__ = mock.Mock(return_value=mock_tabs[2])
        mock_tabs[2].__exit__ = mock.Mock(return_value=None)

        # Mock container context manager
        mock_container = mock.Mock()
        mock_container.__enter__ = mock.Mock(return_value=mock_container)
        mock_container.__exit__ = mock.Mock(return_value=None)
        mock_st.container.return_value = mock_container

        # Mock create_agent_tree
        with mock.patch(
            "app.pages.agent_manager.create_agent_tree"
        ) as mock_create_tree:
            mock_dot = mock.Mock()
            mock_dot.source = "graph TD"
            mock_create_tree.return_value = mock_dot

            # Run main
            main()

            # Verify calls
            mock_st.markdown.assert_any_call("# 🌳 Agent Manager")
            mock_st.tabs.assert_called_once()
            mock_create_tree.assert_called_once()
            mock_st.graphviz_chart.assert_called_once_with("graph TD")

    @mock.patch("app.pages.agent_manager.st")
    @pytest.mark.skip_ci
    @pytest.mark.issue_82
    def test_main_tree_error(self, mock_st):
        """Test main function when tree creation fails."""
        # Mock streamlit components
        mock_tabs = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_st.tabs.return_value = mock_tabs

        # Setup session state
        from app.pages.agent_manager import DEFAULT_AGENT_CONFIG

        session_state_dict = {
            "custom_agents": [],
            "agent_config": DEFAULT_AGENT_CONFIG.copy(),
        }

        class MockSessionState(dict):
            def __getattr__(self, name):
                return self[name]

            def __setattr__(self, name, value):
                self[name] = value

            def __contains__(self, name):
                return dict.__contains__(self, name)

        mock_st.session_state = MockSessionState(session_state_dict)

        # Tab contexts
        mock_tabs[0].__enter__ = mock.Mock(return_value=mock_tabs[0])
        mock_tabs[0].__exit__ = mock.Mock(return_value=None)
        mock_tabs[1].__enter__ = mock.Mock(return_value=mock_tabs[1])
        mock_tabs[1].__exit__ = mock.Mock(return_value=None)
        mock_tabs[2].__enter__ = mock.Mock(return_value=mock_tabs[2])
        mock_tabs[2].__exit__ = mock.Mock(return_value=None)

        # Mock create_agent_tree to raise exception
        with mock.patch(
            "app.pages.agent_manager.create_agent_tree"
        ) as mock_create_tree:
            mock_create_tree.side_effect = Exception("Tree creation failed")

            # Run main
            main()

            # Verify error handling
            mock_st.error.assert_called_once_with(
                "Error creating tree visualization: Tree creation failed"
            )
            mock_st.write.assert_called_once_with("Fallback: Using text representation")
            # Check fallback markdowns were called
            mock_st.markdown.assert_any_call("```")

    @mock.patch("app.pages.agent_manager.st")
    @pytest.mark.skip_ci
    @pytest.mark.issue_82
    def test_configure_agents_tab(self, mock_st):
        """Test the configure agents tab functionality."""
        # Mock streamlit components
        mock_tabs = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_st.tabs.return_value = mock_tabs

        # Setup session state
        from app.pages.agent_manager import DEFAULT_AGENT_CONFIG

        session_state_dict = {
            "custom_agents": [],
            "agent_config": DEFAULT_AGENT_CONFIG.copy(),
        }

        class MockSessionState(dict):
            def __getattr__(self, name):
                return self[name]

            def __setattr__(self, name, value):
                self[name] = value

            def __contains__(self, name):
                return dict.__contains__(self, name)

        mock_st.session_state = MockSessionState(session_state_dict)

        # Mock selectbox
        mock_st.selectbox.side_effect = ["luca", "gpt-4o"]  # agent, then model

        # Create column mocks as context managers
        def create_mock_column():
            col = mock.Mock()
            col.__enter__ = mock.Mock(return_value=col)
            col.__exit__ = mock.Mock(return_value=None)
            return col

        mock_cols = [create_mock_column(), create_mock_column(), create_mock_column()]
        mock_st.columns.return_value = mock_cols

        # Tab contexts
        mock_tabs[0].__enter__ = mock.Mock(return_value=mock_tabs[0])
        mock_tabs[0].__exit__ = mock.Mock(return_value=None)
        mock_tabs[1].__enter__ = mock.Mock(return_value=mock_tabs[1])
        mock_tabs[1].__exit__ = mock.Mock(return_value=None)
        mock_tabs[2].__enter__ = mock.Mock(return_value=mock_tabs[2])
        mock_tabs[2].__exit__ = mock.Mock(return_value=None)

        # Run main
        with mock.patch("app.pages.agent_manager.create_agent_tree"):
            main()

            # Verify agent configuration tab
            mock_st.header.assert_any_call("Agent Configuration")
            assert mock_st.selectbox.call_count >= 1

    @mock.patch("app.pages.agent_manager.st")
    @pytest.mark.skip_ci
    @pytest.mark.issue_82
    def test_agent_status_tab(self, mock_st):
        """Test the agent status tab functionality."""
        # Mock streamlit components
        mock_tabs = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_st.tabs.return_value = mock_tabs

        # Setup session state
        from app.pages.agent_manager import DEFAULT_AGENT_CONFIG

        session_state_dict = {
            "custom_agents": [],
            "agent_config": DEFAULT_AGENT_CONFIG.copy(),
        }

        class MockSessionState(dict):
            def __getattr__(self, name):
                return self[name]

            def __setattr__(self, name, value):
                self[name] = value

            def __contains__(self, name):
                return dict.__contains__(self, name)

        mock_st.session_state = MockSessionState(session_state_dict)

        # Tab contexts
        mock_tabs[0].__enter__ = mock.Mock(return_value=mock_tabs[0])
        mock_tabs[0].__exit__ = mock.Mock(return_value=None)
        mock_tabs[1].__enter__ = mock.Mock(return_value=mock_tabs[1])
        mock_tabs[1].__exit__ = mock.Mock(return_value=None)
        mock_tabs[2].__enter__ = mock.Mock(return_value=mock_tabs[2])
        mock_tabs[2].__exit__ = mock.Mock(return_value=None)

        # Run main
        with mock.patch("app.pages.agent_manager.create_agent_tree"):
            main()

            # Verify status tab
            mock_st.header.assert_any_call("Agent Status Dashboard")
            mock_st.metric.assert_called()  # Should create metrics
            mock_st.success.assert_called()  # For active status
            mock_st.warning.assert_called()  # For idle status

    @mock.patch("app.pages.agent_manager.st")
    @pytest.mark.skip_ci
    @pytest.mark.issue_82
    def test_empty_custom_agents(self, mock_st):
        """Test with empty custom agents list."""
        # Mock streamlit components
        mock_tabs = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_st.tabs.return_value = mock_tabs

        # Setup session state
        from app.pages.agent_manager import DEFAULT_AGENT_CONFIG

        # Empty custom agents
        session_state_dict = {
            "custom_agents": [],
            "agent_config": DEFAULT_AGENT_CONFIG.copy(),
        }

        class MockSessionState(dict):
            def __getattr__(self, name):
                return self[name]

            def __setattr__(self, name, value):
                self[name] = value

            def __contains__(self, name):
                return dict.__contains__(self, name)

        mock_st.session_state = MockSessionState(session_state_dict)

        # Tab contexts
        mock_tabs[0].__enter__ = mock.Mock(return_value=mock_tabs[0])
        mock_tabs[0].__exit__ = mock.Mock(return_value=None)
        mock_tabs[1].__enter__ = mock.Mock(return_value=mock_tabs[1])
        mock_tabs[1].__exit__ = mock.Mock(return_value=None)
        mock_tabs[2].__enter__ = mock.Mock(return_value=mock_tabs[2])
        mock_tabs[2].__exit__ = mock.Mock(return_value=None)

        # Mock create_agent_tree
        with mock.patch(
            "app.pages.agent_manager.create_agent_tree"
        ) as mock_create_tree:
            mock_dot = mock.Mock()
            mock_dot.source = "graph TD"
            mock_create_tree.return_value = mock_dot

            # Run main
            main()

            # Should still work with empty custom agents
            mock_create_tree.assert_called_once()

    @mock.patch("app.pages.agent_manager.st")
    @pytest.mark.skip_ci
    @pytest.mark.issue_82
    def test_create_agent_tree(self, mock_st):
        """Test the create_agent_tree function."""
        # Setup session state
        from app.pages.agent_manager import DEFAULT_AGENT_CONFIG

        session_state_dict = {
            "agent_config": DEFAULT_AGENT_CONFIG.copy(),
        }

        class MockSessionState(dict):
            def __getattr__(self, name):
                return self[name]

        mock_st.session_state = MockSessionState(session_state_dict)

        # Create tree
        tree = create_agent_tree()

        # Verify it's a graphviz object
        assert hasattr(tree, "node")
        assert hasattr(tree, "edge")
        assert hasattr(tree, "source")

        # Check that all agents are in the tree
        for agent_id in DEFAULT_AGENT_CONFIG.keys():
            assert agent_id in tree.source
