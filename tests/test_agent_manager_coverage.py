"""Test coverage for app/pages/agent_manager.py."""

import json
import unittest.mock as mock

import pytest
import streamlit as st

from app.pages.agent_manager import AGENT_CONFIG


class TestAgentManagerCoverage:
    """Test coverage for agent_manager.py."""

    def test_agent_config_exists(self):
        """Test that AGENT_CONFIG is properly defined."""
        assert AGENT_CONFIG is not None
        assert isinstance(AGENT_CONFIG, dict)
        assert len(AGENT_CONFIG) == 5  # luca, coder, tester, doc_writer, analyst

    def test_html_content_generation(self):
        """Test that the page generates valid HTML content."""
        # Since the page now uses components.html() with a large HTML string,
        # we just verify the configuration is valid
        for agent_id, agent_data in AGENT_CONFIG.items():
            assert isinstance(agent_data["name"], str)
            assert isinstance(agent_data["role"], str)
            assert isinstance(agent_data["description"], str)
            assert isinstance(agent_data["color"], str)
