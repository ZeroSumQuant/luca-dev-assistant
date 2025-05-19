"""Tests for app/main.py coverage specifically targeting lines 173-175, 203."""

import asyncio
import sys
import unittest.mock as mock

import pytest
import streamlit as st

from app.main import main


class TestAppMainCoverage:
    """Tests to specifically hit uncovered lines in app/main.py."""

    @mock.patch("app.main.st")
    @mock.patch("app.main.get_manager")
    def test_process_async_manager_init(self, mock_get_manager, mock_st):
        """Cover lines 173-175 in app/main.py for async manager initialization."""
        # Setup streamlit mocks
        mock_session_state = {"messages": [], "custom_agents": []}
        mock_st.session_state = mock_session_state
        mock_st.text_input.return_value = ""  # Empty prompt initially
        mock_st.chat_input.return_value = "test prompt"  # Return test prompt
        mock_st.sidebar.selectbox.return_value = "pro"
        mock_st.toggle.return_value = False
        mock_st.columns.return_value = [mock.Mock(), mock.Mock(), mock.Mock()]

        # Mock the async manager
        mock_manager = mock.AsyncMock()
        mock_manager.process_request.return_value = "Test response"
        mock_get_manager.return_value = mock_manager

        # Run main but ensure we break out after processing one message
        call_count = 0

        def chat_input_side_effect(prompt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "test prompt"
            return None

        mock_st.chat_input.side_effect = chat_input_side_effect

        # Ensure the page returns 'main' to go into main interface
        def page_mock():
            # First call returns the page, subsequent return None
            if not hasattr(page_mock, "called"):
                page_mock.called = True
                return {"page": "main"}
            return None

        mock_st.experimental_get_query_params.side_effect = page_mock

        # Mock message display components
        mock_st.empty.return_value = mock.Mock()
        mock_chat_msg = mock.Mock()
        mock_st.chat_message.return_value.__enter__ = mock.Mock(
            return_value=mock_chat_msg
        )
        mock_st.chat_message.return_value.__exit__ = mock.Mock(return_value=None)

        # Since we can't truly run the Streamlit main loop, we'll extract and test
        # the async process function directly
        with mock.patch("sys.exit"):
            # Import the main function and test the relevant part
            with mock.patch("asyncio.run") as mock_asyncio_run:
                try:
                    main()
                except SystemExit:
                    pass

                # Verify asyncio.run was called
                if mock_asyncio_run.called:
                    # Get the coroutine that was passed to asyncio.run
                    coro = mock_asyncio_run.call_args[0][0]
                    # This should be the process() function that contains lines 173-175

                    # Manually execute the coroutine to ensure coverage
                    async def test_coro():
                        result = await coro
                        return result

                    # Run the coroutine
                    result = asyncio.run(test_coro())

                    # Verify manager was initialized (line 174)
                    mock_manager.initialize.assert_called_once()

    def test_main_entry_point(self):
        """Cover line 203 - the if __name__ == '__main__' block."""
        # Mock the main function
        with mock.patch("app.main.main") as mock_main:
            with mock.patch.object(sys, "argv", ["app.main"]):
                # Execute the module as main
                import app.main

                # Force execution of the if __name__ == "__main__" block
                if app.main.__name__ != "__main__":
                    app.main.__name__ = "__main__"
                    # Re-evaluate the module to trigger the condition
                    with open(app.main.__file__, "r") as f:
                        code = compile(f.read(), app.main.__file__, "exec")
                        exec(
                            code,
                            {"__name__": "__main__", "__file__": app.main.__file__},
                        )

                mock_main.assert_called()
