"""Comprehensive tests for orb showcase page to improve coverage."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add tests directory to path to import helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers.streamlit_mock import create_streamlit_mock


class TestOrbShowcaseComprehensive:
    """Comprehensive test suite for orb showcase page."""

    @pytest.fixture(autouse=True)
    def setup_streamlit_mocks(self):
        """Set up Streamlit mocks before each test."""
        # Create comprehensive mock
        self.mock_st = create_streamlit_mock()

        # Add additional mocks for interactive elements
        self.mock_st.code = MagicMock()
        self.mock_st.subheader = MagicMock()
        self.mock_st.selectbox = MagicMock(return_value="luca")

        # Use generators for side effects to provide unlimited values
        def checkbox_generator():
            while True:
                yield True
                yield False

        def slider_generator():
            values = [120, 1.0, 150, 0.8]
            idx = 0
            while True:
                yield values[idx % len(values)]
                idx += 1

        checkbox_gen = checkbox_generator()
        slider_gen = slider_generator()
        self.mock_st.checkbox = MagicMock(
            side_effect=lambda *args, **kwargs: next(checkbox_gen)
        )
        self.mock_st.slider = MagicMock(
            side_effect=lambda *args, **kwargs: next(slider_gen)
        )

        # Setup tabs with proper context managers
        self.tab_contexts = []
        for i in range(4):
            tab_ctx = MagicMock()
            tab_ctx.__enter__ = MagicMock(return_value=tab_ctx)
            tab_ctx.__exit__ = MagicMock(return_value=None)
            tab_ctx.entered = False

            # Track when tab is entered
            def make_enter(ctx):
                def enter(*args):
                    ctx.entered = True
                    return ctx

                return enter

            tab_ctx.__enter__ = make_enter(tab_ctx)
            self.tab_contexts.append(tab_ctx)

        self.mock_st.tabs.return_value = self.tab_contexts

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

    def test_all_tabs_coverage(self):
        """Test that all tabs in the showcase are covered."""
        import app.pages.orb_showcase

        # Check all tabs were created
        self.mock_st.tabs.assert_called_once()
        tabs_call = self.mock_st.tabs.call_args[0][0]
        assert len(tabs_call) == 4
        assert "All Orbs" in tabs_call
        assert "Individual Orbs" in tabs_call
        assert "Size Variations" in tabs_call
        assert "Code Example" in tabs_call

    def test_tab1_all_orbs(self):
        """Test tab 1 - All Orbs display."""
        import app.pages.orb_showcase

        # Should render orbs for all 5 types
        # Check that render was called multiple times
        assert self.mock_render.call_count >= 5

    def test_tab2_individual_orbs(self):
        """Test tab 2 - Individual Orb controls."""
        import app.pages.orb_showcase

        # Check interactive controls were created
        self.mock_st.selectbox.assert_called()
        assert self.mock_st.checkbox.call_count >= 2  # show_label, is_selected
        assert self.mock_st.slider.call_count >= 2  # size, scale

    def test_tab3_size_variations(self):
        """Test tab 3 - Size Variations."""
        import app.pages.orb_showcase

        # Should show multiple size variations
        # Check for size-related renders
        size_calls = [
            call
            for call in self.mock_render.call_args_list
            if "size" in call[1] and call[1]["size"] != 120
        ]
        assert len(size_calls) > 0

    def test_tab4_code_example(self):
        """Test tab 4 - Code Example."""
        import app.pages.orb_showcase

        # Should show code example
        self.mock_st.code.assert_called()
        code_call = self.mock_st.code.call_args[0][0]
        assert "render_constellation_orb" in code_call
        assert "orb_type=" in code_call

    def test_page_structure(self):
        """Test overall page structure."""
        import app.pages.orb_showcase

        # Check page config
        self.mock_st.set_page_config.assert_called()

        # Check title
        self.mock_st.title.assert_called()

        # Check markdown content
        assert self.mock_st.markdown.called
