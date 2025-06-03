#!/usr/bin/env python3
"""Launch the Luca Streamlit app."""

import os
import subprocess
import sys


def main():
    """Start the Streamlit application."""
    app_path = os.path.join(os.path.dirname(__file__), "..", "app", "main_modern.py")

    # Ensure Streamlit is installed
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print("Streamlit not found. Installing dependencies...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )

    # Run Streamlit
    try:
        print("🚀 Starting Luca Dev Assistant UI...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
