import subprocess
import sys


def test_luca_cli_runs():
    """Ensure luca.py launches and exits cleanly."""
    result = subprocess.run([sys.executable, "luca.py"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "placeholder" in result.stdout.lower()
