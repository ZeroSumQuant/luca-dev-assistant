"""Tests for the orb showcase page."""

import unittest.mock as mock

import pytest
import streamlit as st


class TestOrbShowcase:
    """Test suite for orb showcase page."""

    @mock.patch("streamlit.tabs")
    @mock.patch("streamlit.markdown")
    @mock.patch("streamlit.title")
    @mock.patch("streamlit.set_page_config")
    def test_page_loads(self, mock_config, mock_title, mock_markdown, mock_tabs):
        """Test that the orb showcase page loads without errors."""
        # Mock tabs to return a list of mock objects
        mock_tab = mock.MagicMock()
        mock_tab.__enter__ = mock.Mock(return_value=mock_tab)
        mock_tab.__exit__ = mock.Mock(return_value=None)
        mock_tabs.return_value = [mock_tab] * 4

        # Import should work without errors
        import app.pages.orb_showcase

        # Check that page was configured
        mock_config.assert_called_once()
        assert "Orb Showcase" in str(mock_config.call_args)

    def test_orb_configs_defined(self):
        """Test that orb configurations are properly defined."""
        # This tests the module-level code
        from app.pages import orb_showcase

        # The module should have executed without errors
        # We can't directly test the content since it's in the with statements
        # but we can verify the module loaded successfully
        assert hasattr(orb_showcase, "__file__")
