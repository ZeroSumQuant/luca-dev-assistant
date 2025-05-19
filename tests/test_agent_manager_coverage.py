"""Test coverage for app/pages/agent_manager.py."""

import json
import unittest.mock as mock

import pytest
import streamlit as st

from app.pages.agent_manager import create_agent_tree, main


class TestAgentManagerCoverage:
    """Test coverage for agent_manager.py to reach 95%."""

    @mock.patch("app.pages.agent_manager.st")
    def test_main_happy_path(self, mock_st):
        """Test the main function with normal execution."""
        # Mock streamlit components
        mock_tabs = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_st.tabs.return_value = mock_tabs

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
            mock_create_tree.side_effect = Exception("Tree error")

            # Run main
            main()

            # Verify error handling
            mock_st.error.assert_called_once()
            # Verify fallback text is shown
            mock_st.markdown.assert_any_call("🧠 Luca (Manager)")

    @mock.patch("app.pages.agent_manager.st")
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

        # Setup tab contexts
        for i, tab in enumerate(mock_tabs):
            tab.__enter__ = mock.Mock(return_value=tab)
            tab.__exit__ = mock.Mock(return_value=None)

        # Mock form elements
        mock_form = mock.Mock()
        mock_form.__enter__ = mock.Mock(return_value=mock_form)
        mock_form.__exit__ = mock.Mock(return_value=None)
        mock_st.form.return_value = mock_form

        mock_st.text_input.side_effect = [
            "NewAgent",
            "Does new things",
            "python3 new_agent.py",
        ]
        mock_st.selectbox.return_value = "general"
        mock_st.form_submit_button.return_value = True

        # Run main
        main()

        # Verify form was created
        mock_st.form.assert_called_once()

        # Verify agent was added to session state
        assert len(mock_st.session_state["custom_agents"]) == 1
        new_agent = mock_st.session_state["custom_agents"][0]
        assert new_agent["name"] == "NewAgent"
        assert new_agent["description"] == "Does new things"

    @mock.patch("app.pages.agent_manager.st")
    def test_agent_status_tab(self, mock_st):
        """Test the agent status tab."""
        # Mock streamlit components
        mock_tabs = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_st.tabs.return_value = mock_tabs

        # Setup session state
        from app.pages.agent_manager import DEFAULT_AGENT_CONFIG

        session_state_dict = {
            "custom_agents": [
                {
                    "name": "TestAgent",
                    "description": "Test description",
                    "domain": "test",
                    "created_at": "2025-05-19T12:00:00",
                }
            ],
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

        # Setup tab contexts
        for tab in mock_tabs:
            tab.__enter__ = mock.Mock(return_value=tab)
            tab.__exit__ = mock.Mock(return_value=None)

        # Run main
        main()

        # Verify status tab shows custom agents
        mock_st.json.assert_called_once()
        json_call_arg = mock_st.json.call_args[0][0]
        assert len(json_call_arg) == 1
        assert json_call_arg[0]["name"] == "TestAgent"

    @mock.patch("app.pages.agent_manager.st")
    def test_empty_custom_agents(self, mock_st):
        """Test when no custom agents exist."""
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

        # Setup tab contexts
        for tab in mock_tabs:
            tab.__enter__ = mock.Mock(return_value=tab)
            tab.__exit__ = mock.Mock(return_value=None)

        # Run main
        main()

        # Verify empty state messages
        mock_st.markdown.assert_any_call("*No custom agents configured yet*")

    def test_create_agent_tree(self):
        """Test the create_agent_tree function."""
        with mock.patch("app.pages.agent_manager.st") as mock_st:
            mock_st.session_state = {
                "custom_agents": [
                    {
                        "name": "CustomAgent",
                        "description": "Custom test agent",
                        "domain": "testing",
                    }
                ]
            }

            # Call create_agent_tree
            dot = create_agent_tree()

            # Verify the graph was created
            assert dot is not None
            assert "Luca" in dot.source
            assert "Manager" in dot.source
            assert "CustomAgent" in dot.source
