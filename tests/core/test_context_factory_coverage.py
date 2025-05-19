"""Tests to improve coverage for context factory module."""

import unittest.mock as mock

import pytest

from luca_core.context.factory import create_async_context_store, create_context_store


class TestContextFactoryCoverage:
    """Test context factory edge cases for coverage."""

    @pytest.mark.asyncio
    async def test_create_async_context_store_invalid_type(self):
        """Test creating context store with invalid type."""
        with pytest.raises(ValueError, match="Unsupported context store type: invalid"):
            await create_async_context_store("invalid")

    def test_create_context_store_sync_with_event_loop(self):
        """Test synchronous creation when event loop is running."""
        # Mock an event loop
        mock_loop = mock.MagicMock()
        mock_store = mock.MagicMock()
        mock_loop.run_until_complete.return_value = mock_store

        with mock.patch("asyncio.get_running_loop", return_value=mock_loop):
            with mock.patch(
                "luca_core.context.factory.create_async_context_store"
            ) as mock_create:
                mock_create.return_value = mock_store

                # Call the synchronous function
                result = create_context_store("sqlite", "/test/path")

                # Verify loop.run_until_complete was called
                mock_loop.run_until_complete.assert_called_once()

                # Verify we got the store back
                assert result == mock_store
