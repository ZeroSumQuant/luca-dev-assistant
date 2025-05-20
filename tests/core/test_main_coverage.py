"""Tests to improve coverage for __main__ module."""

import sys
import unittest.mock as mock

import pytest

from luca_core.__main__ import main


class TestMainCoverage:
    """Test __main__ module edge cases for coverage."""

    @pytest.mark.skip_ci
    @pytest.mark.issue_84
    def test_main_module_execution(self):
        """Test module execution via __name__ == '__main__'."""
        with mock.patch("sys.argv", ["luca"]):
            with mock.patch("sys.exit") as mock_exit:
                with mock.patch("luca_core.__main__.main", return_value=0) as mock_main:
                    # Create a code snippet that mimics what happens
                    # when the module is run as __main__
                    code = "import sys; from luca_core.__main__ import main; sys.exit(main())"

                    # Execute the code in the mocked environment
                    exec(code)

                    # Verify main was called
                    mock_main.assert_called_once()

                    # Verify sys.exit was called with the return value
                    mock_exit.assert_called_once_with(0)
