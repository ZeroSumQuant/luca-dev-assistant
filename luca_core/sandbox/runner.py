import os
import subprocess
from pathlib import Path
from typing import List, Union


class SandboxTimeoutError(RuntimeError):
    """Raised when the sandboxed subprocess exceeds the wall-clock limit."""

    pass


class SandboxRunner:
    def __init__(self, image: str, workdir: Union[str, Path], timeout: int = 300):
        self.image = image
        self.workdir = str(workdir)
        self.timeout = timeout

    def run(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Execute *cmd* inside the sandbox image under resource caps."""
        try:
            return subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--cpus=1",
                    "--memory=2g",
                    "-v",
                    f"{self.workdir}:/workspace:rw",
                    self.image,
                    *cmd,
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise SandboxTimeoutError(
                f"Sandbox execution exceeded {self.timeout}s: {cmd}"
            ) from exc
