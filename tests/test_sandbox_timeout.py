import shutil
from pathlib import Path

import pytest

from luca_core.sandbox import SandboxRunner, SandboxTimeoutError

IMAGE = "luca-test"  # reuse the slim test image


@pytest.mark.ci
@pytest.mark.skipif(not shutil.which("docker"), reason="Docker not available")
def test_infinite_loop_times_out(tmp_path: Path):
    runner = SandboxRunner(image=IMAGE, workdir=tmp_path, timeout=2)
    with pytest.raises(SandboxTimeoutError):
        runner.run(["python", "-c", "while True: pass"])
