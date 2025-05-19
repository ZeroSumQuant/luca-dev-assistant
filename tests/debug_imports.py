"""Debug import chain to find where AutoGen is coming from."""

import importlib.util
import sys

# Store original import
original_import = __builtins__.__import__


def debug_import(name, *args, **kwargs):
    """Intercept imports to find AutoGen."""
    if "autogen" in name.lower():
        import traceback

        print(f"\n=== IMPORT DETECTED: {name} ===")
        traceback.print_stack()
        print("=== END STACK ===\n")
    return original_import(name, *args, **kwargs)


# Replace the import function
__builtins__.__import__ = debug_import

# Now run pytest
if __name__ == "__main__":
    import pytest

    sys.exit(
        pytest.main(
            [
                "-v",
                "tests/core/test_registry_execute.py::TestToolExecute::test_execute_tool_success",
                "-s",
            ]
        )
    )
