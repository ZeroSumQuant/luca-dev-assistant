"""Tests for orb showcase page."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add tests directory to path to import helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers.streamlit_mock import create_streamlit_mock


class TestOrbShowcase:
    """Test suite for orb showcase page."""

    @pytest.fixture(autouse=True)
    def setup_streamlit_mocks(self):
        """Set up Streamlit mocks before each test."""
        # Create comprehensive mock
        self.mock_st = create_streamlit_mock()

        # Add additional mocks for orb showcase
        self.mock_st.code = MagicMock()
        self.mock_st.subheader = MagicMock()
        self.mock_st.selectbox = MagicMock(return_value="luca")
        self.mock_st.slider = MagicMock(return_value=120)

        # Use a generator for checkbox to provide unlimited values
        def checkbox_generator():
            while True:
                yield True
                yield False

        checkbox_gen = checkbox_generator()
        self.mock_st.checkbox = MagicMock(
            side_effect=lambda *args, **kwargs: next(checkbox_gen)
        )

        # Patch modules before imports
        sys.modules["streamlit"] = self.mock_st
        sys.modules["streamlit.components"] = MagicMock()
        sys.modules["streamlit.components.v1"] = self.mock_st.components.v1

        # Mock the constellation_orb module
        self.mock_render = MagicMock()
        sys.modules["app.components.constellation_orb"] = MagicMock(
            render_constellation_orb=self.mock_render
        )

        yield

        # Clean up
        for module in [
            "app.pages.orb_showcase",
            "app.components.constellation_orb",
            "streamlit",
            "streamlit.components",
            "streamlit.components.v1",
        ]:
            if module in sys.modules:
                del sys.modules[module]

    def test_page_imports(self):
        """Test that the page imports correctly."""
        # Should not raise any errors
        import app.pages.orb_showcase

        # Basic checks that module loaded
        assert hasattr(app.pages.orb_showcase, "__file__")

    def test_page_configuration(self):
        """Test page configuration is set up correctly."""
        # Import the page
        import app.pages.orb_showcase

        # Check that page config was called
        self.mock_st.set_page_config.assert_called()

        # Verify page config parameters
        config_call = self.mock_st.set_page_config.call_args
        assert config_call[1]["page_title"] == "Orb Showcase - LUCA"
        assert config_call[1]["page_icon"] == "🔮"
        assert config_call[1]["layout"] == "wide"

    def test_page_header(self):
        """Test page header elements are created."""
        import app.pages.orb_showcase

        # Check title was set
        self.mock_st.title.assert_called()
        title_call = self.mock_st.title.call_args
        assert "Constellation Orb Showcase" in str(title_call)

    def test_orb_display(self):
        """Test that orbs are displayed."""
        import app.pages.orb_showcase

        # Check that columns were created for layout
        self.mock_st.columns.assert_called()

        # Check that orbs were rendered through render_constellation_orb
        assert self.mock_render.called

        # Should have multiple orb renders
        assert self.mock_render.call_count >= 5  # At least 5 orb types
