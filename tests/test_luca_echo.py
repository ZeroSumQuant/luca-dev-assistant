import sys
from subprocess import PIPE, run


def test_luca_echo():
    """Luca should echo the prompt back (proves FileTool + DockerTool wire-up)."""
    result = run([sys.executable, "luca.py", "Hello"], stdout=PIPE, text=True)
    assert result.returncode == 0
    assert "hello" in result.stdout.lower()
