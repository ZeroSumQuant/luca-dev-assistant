from subprocess import run

def test_bootstrap_runs():
    result = run(
        ["python", "scripts/start_assistant.py"],
        capture_output=True, text=True, check=True
    )
    assert "Luca ready" in result.stdout
    assert "key=✔" in result.stdout
