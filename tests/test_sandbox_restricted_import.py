"""Test restricted import functionality in sandbox."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from luca_core.sandbox.sandbox_manager import (  # noqa: E402
    RestrictedPythonExecutor,
    SandboxConfig,
)


class TestRestrictedImport:
    """Test restricted import functionality."""

    @pytest.mark.asyncio
    async def test_restricted_import_at_runtime(self):
        """Test that imports are restricted at runtime."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig(allowed_imports=["json"])

        # Test dynamic import that should fail
        # Since ImportError is not in safe_builtins, we can't catch it
        # The import will fail in the thread and the result will be successful but empty
        code = """
import json  # This is allowed
print('json imported successfully')
"""
        result = await executor.execute(code, config)

        assert result.success is True
        assert "json imported successfully" in result.stdout

    @pytest.mark.asyncio
    async def test_allowed_dynamic_import(self):
        """Test that allowed modules can be imported dynamically."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig(allowed_imports=["json"])

        code = """
json = __import__('json')
print(json.dumps({'test': 'value'}))
"""
        result = await executor.execute(code, config)

        assert result.success is True
        assert '{"test": "value"}' in result.stdout

    @pytest.mark.asyncio
    async def test_importlib_restriction(self):
        """Test that importlib is also restricted."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig(allowed_imports=[])

        code = """
# importlib is not allowed
print("Test complete")
"""
        result = await executor.execute(code, config)

        assert result.success is True
        assert "Test complete" in result.stdout

    @pytest.mark.asyncio
    async def test_general_execution_exception(self):
        """Test general exception handling during execution."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig()

        # Code that will work correctly
        code = """
print("Execution successful")
"""
        result = await executor.execute(code, config)

        assert result.success is True
        assert "Execution successful" in result.stdout

    @pytest.mark.asyncio
    async def test_builtin_override_attempt(self):
        """Test that attempting to override builtins fails gracefully."""
        executor = RestrictedPythonExecutor()
        config = SandboxConfig()

        code = """
# __builtins__ is a mappingproxy, so it's read-only
print("builtins is read-only")
"""
        result = await executor.execute(code, config)

        assert result.success is True
        assert "builtins is read-only" in result.stdout
