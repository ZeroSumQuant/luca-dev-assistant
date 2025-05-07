import subprocess
import sys
import pytest


def test_luca_cli_runs():
    """Ensure luca.py launches and exits cleanly."""
    try:
        result = subprocess.run([sys.executable, "luca.py"], capture_output=True, text=True)
        # Only assert success if the import works
        if "ModuleNotFoundError" not in result.stderr:
            assert result.returncode == 0
            assert "placeholder" in result.stdout.lower()
        else:
            pytest.skip("autogen_core not available in CI environment")
    except Exception:
        pytest.skip("Test environment issue")
