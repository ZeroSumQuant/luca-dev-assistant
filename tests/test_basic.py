from subprocess import run


def test_bootstrap_runs():
    """Smoke-test: Luca’s bootstrap script should run without crashing
    and print its readiness banner. We don’t care whether the key is ✔ or ✖
    on CI runners—only that the banner appears and exit-code is 0.
    """
    result = run(
        ["python3", "scripts/start_assistant.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Luca ready" in result.stdout
