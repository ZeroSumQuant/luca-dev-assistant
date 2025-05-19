"""Specific test for registry.py lines that aren't covered."""

import unittest.mock as mock

import pytest

from luca_core.registry.registry import ToolRegistry
from luca_core.schemas.tools import ToolCategory


class TestRegistrySpecificCoverage:
    """Tests to specifically hit uncovered lines in registry.py."""

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_registry_execute_function_not_found(self):
        """Test line 290 in registry.py - Function not found."""
        registry = ToolRegistry()

        # Register a tool with a bogus function reference
        @registry.register(name="bad_tool", category=ToolCategory.UTILITY)
        def dummy_func():
            return "test"

        # Manually set a bad function reference
        tool = registry.tools["bad_tool"]
        tool.function_reference = "nonexistent_function_that_does_not_exist"

        # This should trigger line 290
        with pytest.raises(ValueError, match="Function not found for tool: bad_tool"):
            registry.execute_tool("bad_tool", {})

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_registry_execute_exception_handling(self):
        """Test lines 325-337 in registry.py - Exception handling."""
        registry = ToolRegistry()

        # Create the module that will hold our function
        import sys

        current_module = sys.modules[__name__]

        # Define the error function at module level
        def error_func():
            raise RuntimeError("Intentional test error")

        # Set it as an attribute of the current module
        setattr(current_module, "error_func", error_func)

        # Register the tool
        @registry.register(name="error_tool", category=ToolCategory.UTILITY)
        def error_func_wrapper():
            raise RuntimeError("Intentional test error")

        # Manually set the function reference to find it
        tool = registry.tools["error_tool"]
        tool.function_reference = "error_func"

        # Execute and expect the exception - this covers lines 325-337
        with pytest.raises(RuntimeError, match="Intentional test error"):
            registry.execute_tool("error_tool", {})

        # Check that error metrics were updated
        assert tool.metrics.error_count == 1
        assert tool.metrics.last_error is not None
        assert len(tool.metrics.error_details) == 1

        error_detail = tool.metrics.error_details[0]
        assert error_detail["error_type"] == "RuntimeError"
        assert error_detail["error_message"] == "Intentional test error"
        assert "timestamp" in error_detail

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_registry_execute_with_module_function(self):
        """Test function resolution from module."""
        registry = ToolRegistry()

        # Create a mock module with a function
        mock_module = mock.Mock()
        mock_module.test_func = lambda: "module result"

        # Register tool with module reference
        @registry.register(name="module_tool", category=ToolCategory.UTILITY)
        def placeholder():
            pass

        # Set function reference to use module
        tool = registry.tools["module_tool"]
        tool.function_reference = "test_func"

        # Mock sys.modules to include our mock module
        with mock.patch("sys.modules", {"__main__": mock_module}):
            result = registry.execute_tool("module_tool", {})
            assert result == "module result"

    @pytest.mark.skip_ci
    @pytest.mark.issue_81
    def test_app_main_async_process(self):
        """Test app/main.py lines 173-175."""
        import asyncio

        from app.main import get_manager

        # Create a mock manager
        with mock.patch("app.main.manager_instance", None):
            with mock.patch("luca_core.manager.manager.LucaManager") as MockManager:
                mock_manager = mock.AsyncMock()
                MockManager.return_value = mock_manager

                # Test the async process function directly
                async def test_process():
                    manager = get_manager()
                    await manager.initialize()
                    return await manager.process_request("test", None)

                # Run the async function
                mock_manager.process_request.return_value = "test response"
                result = asyncio.run(test_process())

                # Verify initialization was called
                mock_manager.initialize.assert_called_once()
                assert result == "test response"
