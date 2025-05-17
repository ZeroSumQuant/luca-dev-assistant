import shutil
import subprocess
from pathlib import Path

import pytest

from luca_core.sandbox import SandboxRunner, SandboxTimeoutError

IMAGE = "luca-test"


def _image_available(name: str) -> bool:
    """Return True if *name* docker image is present locally."""
    try:
        return (
            subprocess.run(
                ["docker", "image", "inspect", name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )
    except FileNotFoundError:
        return False


@pytest.mark.ci
@pytest.mark.skipif(
    not (shutil.which("docker") and _image_available(IMAGE)),
    reason="Docker or test image not available",
)
def test_infinite_loop_times_out(tmp_path: Path):
    runner = SandboxRunner(image=IMAGE, workdir=tmp_path, timeout=2)
    with pytest.raises(SandboxTimeoutError):
        runner.run(["python", "-c", "while True: pass"])
