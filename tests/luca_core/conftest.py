"""Configuration file for pytest to run luca_core tests."""

import os
import sys

# Add the project root directory to the Python path for all tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
