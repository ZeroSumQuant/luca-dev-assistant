import os
import shutil
import signal
import subprocess
import tempfile
import textwrap
import time


class SandboxTimeoutError(RuntimeError):
    pass


class SandboxRunner:
    def __init__(self, image: str = "luca-sandbox"):
        self.image = image
        self.workdir = tempfile.mkdtemp(prefix="luca-sandbox-")

    def cleanup(self):
        """Clean up the temporary workspace."""
        if self.workdir and os.path.exists(self.workdir):
            shutil.rmtree(self.workdir)

    def run(self, cmd: list[str]) -> subprocess.CompletedProcess:
        """Execute *cmd* inside the sandbox image with a hard 300-s wall clock."""
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
                timeout=300,
            )
        except subprocess.TimeoutExpired as exc:
            raise SandboxTimeoutError(
                f"Sandbox execution exceeded 300 s: {cmd}"
            ) from exc
