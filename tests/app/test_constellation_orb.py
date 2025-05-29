"""Tests for the constellation orb component."""

import unittest.mock as mock

import pytest

from app.components.constellation_orb import render_constellation_orb, show_orb_gallery


class TestConstellationOrb:
    """Test suite for constellation orb component."""

    def test_render_constellation_orb_default(self):
        """Test rendering orb with default parameters."""
        with mock.patch("streamlit.components.v1.html") as mock_html:
            result = render_constellation_orb()

            # Check that html was called
            mock_html.assert_called_once()

            # Check the HTML content
            html_content = mock_html.call_args[0][0]
            assert "logo-container" in html_content
            assert "orb-inner" in html_content
            assert "LUCA" in html_content

    def test_render_constellation_orb_custom(self):
        """Test rendering orb with custom parameters."""
        with mock.patch("streamlit.components.v1.html") as mock_html:
            result = render_constellation_orb(
                orb_type="coder",
                size=150,
                scale=0.8,
                label_text="Custom Coder",
                clickable=False,
                selected=True,
                show_label=False,
            )

            # Check that html was called
            mock_html.assert_called_once()

            # Check the HTML content reflects custom params
            html_content = mock_html.call_args[0][0]
            assert "150px" in html_content
            assert "scale(0.8)" in html_content
            assert "Custom Coder" in html_content
            assert "'pointer' if clickable else 'default'" in html_content
            assert "display: none;" in html_content  # label hidden

    def test_render_all_orb_types(self):
        """Test rendering all different orb types."""
        orb_types = ["luca", "coder", "tester", "doc", "analyst"]

        with mock.patch("streamlit.components.v1.html") as mock_html:
            for orb_type in orb_types:
                render_constellation_orb(orb_type=orb_type)

            # Should be called once for each type
            assert mock_html.call_count == len(orb_types)

    @mock.patch("streamlit.columns")
    @mock.patch("streamlit.markdown")
    @mock.patch("streamlit.title")
    @mock.patch("streamlit.set_page_config")
    def test_show_orb_gallery(
        self, mock_config, mock_title, mock_markdown, mock_columns
    ):
        """Test the orb gallery display function."""
        # Mock columns to return context managers
        mock_col = mock.MagicMock()
        mock_col.__enter__ = mock.Mock(return_value=mock_col)
        mock_col.__exit__ = mock.Mock(return_value=None)
        mock_columns.return_value = [mock_col] * 5

        with mock.patch(
            "app.components.constellation_orb.render_constellation_orb"
        ) as mock_render:
            show_orb_gallery()

            # Check page config was set
            mock_config.assert_called_once()

            # Check title was set
            mock_title.assert_called_once_with("Constellation Orb Gallery")

            # Check orbs were rendered (5 in normal state + 5 in selected state)
            assert mock_render.call_count == 10
