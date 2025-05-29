"""Tests for the modern main Streamlit UI."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add tests directory to path to import helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers.streamlit_mock import MockSessionState, create_streamlit_mock


class TestMainModern:
    """Test suite for main_modern.py."""

    @pytest.fixture(autouse=True)
    def setup_streamlit_mocks(self):
        """Set up Streamlit mocks before each test."""
        # Create comprehensive mock
        self.mock_st = create_streamlit_mock()

        # Add additional mocks specific to main_modern
        self.mock_st.sidebar.page_link = MagicMock()
        self.mock_st.sidebar.divider = MagicMock()
        self.mock_st.sidebar.selectbox = MagicMock(return_value="Quantitative Trading")
        self.mock_st.sidebar.markdown = MagicMock()
        self.mock_st.sidebar.button = MagicMock(return_value=False)
        self.mock_st.sidebar.title = MagicMock()

        # Mock form and its methods
        mock_form = MagicMock()
        mock_form.__enter__ = MagicMock(return_value=mock_form)
        mock_form.__exit__ = MagicMock(return_value=None)
        mock_form.text_area = MagicMock(return_value="")
        mock_form.form_submit_button = MagicMock(return_value=False)
        self.mock_st.form = MagicMock(return_value=mock_form)

        # Mock spinner
        mock_spinner = MagicMock()
        mock_spinner.__enter__ = MagicMock(return_value=mock_spinner)
        mock_spinner.__exit__ = MagicMock(return_value=None)
        self.mock_st.spinner = MagicMock(return_value=mock_spinner)

        # Additional methods
        self.mock_st.rerun = MagicMock()
        self.mock_st.page_link = MagicMock()
        self.mock_st.divider = MagicMock()

        # Patch modules
        sys.modules["streamlit"] = self.mock_st
        sys.modules["streamlit.components"] = MagicMock()
        sys.modules["streamlit.components.v1"] = self.mock_st.components.v1

        yield

        # Clean up
        for module in [
            "app.main_modern",
            "streamlit",
            "streamlit.components",
            "streamlit.components.v1",
        ]:
            if module in sys.modules:
                del sys.modules[module]

    def test_imports_and_initialization(self):
        """Test that the module imports and initializes correctly."""
        # Import should not raise any errors
        import app.main_modern

        # Page config should be called
        assert self.mock_st.set_page_config.called

        # Session state should be initialized
        assert hasattr(self.mock_st.session_state, "messages")
        assert hasattr(self.mock_st.session_state, "input_key")
        assert hasattr(self.mock_st.session_state, "selected_model")
        assert hasattr(self.mock_st.session_state, "show_model_selector")

    def test_get_icon_function(self):
        """Test the get_icon helper function."""
        import app.main_modern

        # Test known icons
        assert (
            app.main_modern.get_icon("chart")
            == '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>'
        )
        assert (
            app.main_modern.get_icon("trending")
            == '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>'
        )
        assert (
            app.main_modern.get_icon("flask")
            == '<path d="M10 2v8L8 14c-1 2-1 4 0 6a5 5 0 0 0 8 0c1-2 1-4 0-6l-2-4V2"></path><path d="M8.5 2h7"></path><path d="M7 16h10"></path>'
        )
        assert (
            app.main_modern.get_icon("target")
            == '<circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle>'
        )

        # Test unknown icon
        assert app.main_modern.get_icon("unknown") == ""

    def test_page_structure_created(self):
        """Test that the page structure is created on import."""
        import app.main_modern

        # Check that CSS was injected
        assert self.mock_st.markdown.called
        markdown_calls = [
            call
            for call in self.mock_st.markdown.call_args_list
            if call[0][0] and "@import url" in str(call[0][0])
        ]
        assert len(markdown_calls) > 0

        # Check columns were created
        assert self.mock_st.columns.called

        # Check sidebar was configured
        # Note: sidebar operations are done directly on sidebar object
        assert self.mock_st.sidebar.page_link.called or self.mock_st.page_link.called

    def test_streamlit_components_used(self):
        """Test that Streamlit components are properly utilized."""
        import app.main_modern

        # Check that HTML components are used for UI
        assert self.mock_st.components.v1.html.called

        # Check form was created
        assert self.mock_st.form.called

        # Check text area was called either directly or through form
        # main_modern may use different approaches
        assert self.mock_st.text_area.called or (
            hasattr(self.mock_st.form.return_value, "text_area")
            and self.mock_st.form.return_value.text_area.called
        )

    def test_model_selector_ui(self):
        """Test model selector UI elements."""
        import app.main_modern

        # Check that model selector UI elements are rendered
        html_calls = self.mock_st.components.v1.html.call_args_list
        model_selector_calls = [
            call for call in html_calls if "model-dropdown" in str(call[0][0])
        ]
        assert len(model_selector_calls) > 0
