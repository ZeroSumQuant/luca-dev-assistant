"""Tests for the constellation orb component."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add tests directory to path to import helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers.streamlit_mock import create_streamlit_mock


class TestConstellationOrb:
    """Test suite for constellation orb component."""

    @pytest.fixture(autouse=True)
    def setup_streamlit_mocks(self):
        """Set up Streamlit mocks before each test."""
        # Create comprehensive mock
        self.mock_st = create_streamlit_mock()

        # Patch modules before imports
        sys.modules["streamlit"] = self.mock_st
        sys.modules["streamlit.components"] = MagicMock()
        sys.modules["streamlit.components.v1"] = self.mock_st.components.v1

        yield

        # Clean up
        for module in [
            "app.components.constellation_orb",
            "streamlit",
            "streamlit.components",
            "streamlit.components.v1",
        ]:
            if module in sys.modules:
                del sys.modules[module]

    def test_render_constellation_orb_default(self):
        """Test rendering orb with default parameters."""
        from app.components.constellation_orb import render_constellation_orb

        # Clear previous calls
        self.mock_st.components.v1.html.reset_mock()

        # Call function
        render_constellation_orb()

        # Check that html was called
        self.mock_st.components.v1.html.assert_called_once()

        # Check the HTML content
        html_content = self.mock_st.components.v1.html.call_args[0][0]
        assert "logo-container" in html_content
        assert "orb-inner" in html_content
        assert "LUCA" in html_content

    def test_render_constellation_orb_custom(self):
        """Test rendering orb with custom parameters."""
        from app.components.constellation_orb import render_constellation_orb

        # Clear previous calls
        self.mock_st.components.v1.html.reset_mock()

        # Call with custom params
        render_constellation_orb(
            orb_type="coder",
            size=150,
            scale=0.8,
            label_text="Custom Coder",
            clickable=False,
            selected=True,
            show_label=False,
        )

        # Check that html was called
        self.mock_st.components.v1.html.assert_called_once()

        # Check the HTML content reflects custom params
        html_content = self.mock_st.components.v1.html.call_args[0][0]
        assert "150px" in html_content
        assert "scale(0.8)" in html_content
        assert "Custom Coder" in html_content
        assert "cursor: default;" in html_content  # clickable=False
        assert "display: none;" in html_content  # label hidden

    def test_render_all_orb_types(self):
        """Test rendering all different orb types."""
        from app.components.constellation_orb import render_constellation_orb

        orb_types = ["luca", "coder", "tester", "doc", "analyst"]

        # Clear previous calls
        self.mock_st.components.v1.html.reset_mock()

        for orb_type in orb_types:
            render_constellation_orb(orb_type=orb_type)

        # Should be called once for each type
        assert self.mock_st.components.v1.html.call_count == len(orb_types)

    def test_show_orb_gallery(self):
        """Test the orb gallery display function."""
        from app.components.constellation_orb import show_orb_gallery

        # Clear previous calls
        self.mock_st.set_page_config.reset_mock()
        self.mock_st.title.reset_mock()
        self.mock_st.components.v1.html.reset_mock()

        # Call the gallery function
        show_orb_gallery()

        # Check page config was set
        self.mock_st.set_page_config.assert_called_once()

        # Check title was set
        self.mock_st.title.assert_called_once_with("Constellation Orb Gallery")

        # Check orbs were rendered (5 in normal state + 5 in selected state)
        # Each orb type is shown twice (normal and selected)
        assert self.mock_st.components.v1.html.call_count == 10
