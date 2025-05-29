"""Tests for the agent manager Streamlit page."""

import json
import unittest.mock as mock

import pytest

from app.pages.agent_manager import AGENT_CONFIG


class TestAgentManager:
    """Test suite for agent manager functionality."""

    def test_agent_config(self):
        """Test that agent configuration is properly structured."""
        assert "luca" in AGENT_CONFIG
        assert "coder" in AGENT_CONFIG
        assert "tester" in AGENT_CONFIG
        assert "doc_writer" in AGENT_CONFIG
        assert "analyst" in AGENT_CONFIG

        # Check structure of each agent
        for agent_id, agent in AGENT_CONFIG.items():
            assert "name" in agent
            assert "role" in agent
            assert "description" in agent
            assert "color" in agent

        # Verify specific agent details with new roles
        assert AGENT_CONFIG["luca"]["role"] == "Lead Universal Coding Assistant"
        assert AGENT_CONFIG["coder"]["role"] == "Code Generation Specialist"
        assert AGENT_CONFIG["tester"]["role"] == "Quality Assurance Engineer"
        assert AGENT_CONFIG["doc_writer"]["role"] == "Documentation Specialist"
        assert AGENT_CONFIG["analyst"]["role"] == "Code Analysis Expert"

    def test_agent_colors(self):
        """Test that agents have appropriate color schemes."""
        assert AGENT_CONFIG["luca"]["color"] == "main"
        assert AGENT_CONFIG["coder"]["color"] == "coder"
        assert AGENT_CONFIG["tester"]["color"] == "tester"
        assert AGENT_CONFIG["doc_writer"]["color"] == "doc"
        assert AGENT_CONFIG["analyst"]["color"] == "analyst"

    def test_agent_config_json_serializable(self):
        """Test that agent config can be serialized to JSON."""
        # This should not raise an exception
        json_str = json.dumps(AGENT_CONFIG)
        assert isinstance(json_str, str)

        # Can be loaded back
        loaded = json.loads(json_str)
        assert loaded == AGENT_CONFIG
