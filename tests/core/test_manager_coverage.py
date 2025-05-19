"""Tests to improve coverage for manager module."""

import pytest

from luca_core.manager.manager import LucaManager, ResponseOptions
from luca_core.schemas.context import TaskResult


class TestManagerCoverage:
    """Test manager edge cases for coverage."""

    @pytest.mark.asyncio
    async def test_aggregate_results_empty(self):
        """Test aggregating empty results."""
        manager = LucaManager()
        options = ResponseOptions(verbose=False, learning_mode="pro")
        result = await manager._aggregate_results([], options)
        assert result == "I couldn't process your request. Please try again."

    @pytest.mark.asyncio
    async def test_aggregate_results_all_failures(self):
        """Test aggregating results when all failed."""
        manager = LucaManager()
        options = ResponseOptions(verbose=False, learning_mode="pro")

        # Create failed results
        results = [
            TaskResult(task_id="task1", success=False, result="", error="Error 1"),
            TaskResult(task_id="task2", success=False, result="", error="Error 2"),
        ]

        result = await manager._aggregate_results(results, options)
        assert (
            result
            == "I processed your request, but encountered errors and couldn't produce results."
        )

    @pytest.mark.asyncio
    async def test_aggregate_results_success(self):
        """Test aggregating successful results."""
        manager = LucaManager()
        options = ResponseOptions(verbose=False, learning_mode="pro")

        # Create successful results
        results = [
            TaskResult(task_id="task1", success=True, result="Result 1", error=None),
            TaskResult(task_id="task2", success=True, result="Result 2", error=None),
        ]

        result = await manager._aggregate_results(results, options)
        assert result == "Result 1\n\nResult 2"
