"""Tests to improve coverage for manager module."""

import unittest.mock as mock

import pytest

from luca_core.manager.manager import LucaManager, ResponseOptions
from luca_core.schemas.context import TaskResult


class TestManagerCoverage:
    """Test manager edge cases for coverage."""

    @pytest.mark.asyncio
    async def test_aggregate_results_empty(self):
        """Test aggregating empty results."""
        # Create mock context store
        mock_context_store = mock.AsyncMock()
        manager = LucaManager(context_store=mock_context_store)
        options = ResponseOptions(verbose=False, learning_mode="pro")
        result = await manager._aggregate_results([], options)
        assert result == "I couldn't process your request. Please try again."

    @pytest.mark.asyncio
    async def test_aggregate_results_all_failures(self):
        """Test aggregating results when all failed."""
        # Create mock context store
        mock_context_store = mock.AsyncMock()
        manager = LucaManager(context_store=mock_context_store)
        options = ResponseOptions(verbose=False, learning_mode="pro")

        # Create failed results
        results = [
            TaskResult(
                task_id="task1",
                success=False,
                result="",
                error_message="Error 1",
                execution_time_ms=100,
            ),
            TaskResult(
                task_id="task2",
                success=False,
                result="",
                error_message="Error 2",
                execution_time_ms=200,
            ),
        ]

        result = await manager._aggregate_results(results, options)
        assert (
            result
            == "I processed your request, but encountered errors and couldn't produce results."
        )

    @pytest.mark.asyncio
    async def test_aggregate_results_success(self):
        """Test aggregating successful results."""
        # Create mock context store
        mock_context_store = mock.AsyncMock()
        manager = LucaManager(context_store=mock_context_store)
        options = ResponseOptions(verbose=False, learning_mode="pro")

        # Create successful results
        results = [
            TaskResult(
                task_id="task1",
                success=True,
                result="Result 1",
                error_message=None,
                execution_time_ms=100,
            ),
            TaskResult(
                task_id="task2",
                success=True,
                result="Result 2",
                error_message=None,
                execution_time_ms=200,
            ),
        ]

        result = await manager._aggregate_results(results, options)
        assert result == "Result 1\n\nResult 2"
