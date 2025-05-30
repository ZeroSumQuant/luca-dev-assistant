"""Tests for the fingerprint plugin."""

from pathlib import Path

import pytest

from fingerprint import build_fingerprints


def test_fingerprint_returns_records(tmp_path, monkeypatch):
    """Test that fingerprint correctly analyzes Python files."""
    # Create a dummy Python file
    dummy = tmp_path / "foo.py"
    dummy.write_text("def bar(): pass\n")

    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Run fingerprint analysis
    fps = build_fingerprints(tmp_path)

    # Verify results
    assert fps, "Should return at least one fingerprint"
    assert fps[0]["path"].endswith("foo.py"), "Should find our test file"
    assert "bar" in fps[0]["funcs"], "Should detect the bar function"
    assert fps[0]["classes"] == [], "Should have no classes"


def test_fingerprint_caching(tmp_path, monkeypatch):
    """Test that fingerprint caching works correctly."""
    # Create a dummy Python file
    dummy = tmp_path / "test.py"
    dummy.write_text("class TestClass: pass\n")

    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # First run - should analyze the file
    fps1 = build_fingerprints(tmp_path)
    assert len(fps1) == 1
    assert "TestClass" in fps1[0]["classes"]

    # Check that cache was created
    cache_file = tmp_path / ".omniscience" / "cache.json"
    assert cache_file.exists()

    # Second run - should still return results (from cache)
    fps2 = build_fingerprints(tmp_path)
    assert len(fps2) == 1
    assert fps2[0] == fps1[0]


def test_fingerprint_plugin_integration():
    """Test that the fingerprint plugin can be imported and run."""
    from fingerprint import FingerprintPlugin
    from omn_plugins import _PLUGINS

    # Verify plugin is registered
    assert any(p.__name__ == "FingerprintPlugin" for p in _PLUGINS)

    # Test that plugin can run without errors
    plugin = FingerprintPlugin()
    output = plugin.run()

    # Should return a string with the expected header
    assert output.startswith("📇 FINGERPRINT INDEX")
