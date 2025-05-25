#!/usr/bin/env python3
"""Real-time code validation watchdog for LUCA project."""

import ast
import importlib.util
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class CodeValidationHandler(FileSystemEventHandler):
    """Handler for validating Python code changes in real-time."""

    def __init__(self, project_root: Path):
        """Initialize the validation handler."""
        self.project_root = project_root
        self.errors: Dict[str, List[str]] = {}
        self.last_check: Dict[str, float] = {}

        # Colors for terminal output
        self.RED = "\033[0;31m"
        self.GREEN = "\033[0;32m"
        self.YELLOW = "\033[1;33m"
        self.NC = "\033[0m"  # No Color

        # Add project root to sys.path for import validation
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only check Python files
        if file_path.suffix != ".py":
            return

        # Skip test files and hidden files
        if "test_" in file_path.name or file_path.name.startswith("."):
            return

        # Debounce - only check if more than 0.5 seconds since last check
        current_time = time.time()
        last_time = self.last_check.get(str(file_path), 0)
        if current_time - last_time < 0.5:
            return

        self.last_check[str(file_path)] = current_time
        self.validate_file(file_path)

    def validate_file(self, file_path: Path) -> bool:
        """Validate a Python file for syntax and import errors."""
        relative_path = file_path.relative_to(self.project_root)

        try:
            # Read the file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Clear previous errors for this file
            self.errors[str(relative_path)] = []

            # Check for syntax errors
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                self.report_syntax_error(relative_path, e)
                return False

            # Check imports
            import_errors = self.check_imports(tree, file_path)
            if import_errors:
                self.errors[str(relative_path)].extend(import_errors)
                self.report_import_errors(relative_path, import_errors)
                return False

            # If we get here, the file is valid
            if (
                str(relative_path) in self.errors
                and not self.errors[str(relative_path)]
            ):
                del self.errors[str(relative_path)]

            self.report_success(relative_path)
            return True

        except Exception as e:
            self.report_general_error(relative_path, e)
            return False

    def check_imports(self, tree: ast.AST, file_path: Path) -> List[str]:
        """Check if all imports in the file are valid."""
        errors = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if not self.is_valid_import(alias.name):
                        errors.append(
                            f"Line {node.lineno}: Cannot import '{alias.name}'"
                        )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                # Skip relative imports for now
                if node.level > 0:
                    continue

                if module and not self.is_valid_import(module):
                    errors.append(f"Line {node.lineno}: Cannot import from '{module}'")

        return errors

    def is_valid_import(self, module_name: str) -> bool:
        """Check if a module can be imported."""
        try:
            # Try to find the module spec
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False

    def report_syntax_error(self, file_path: Path, error: SyntaxError):
        """Report a syntax error with helpful formatting."""
        print(f"\n{self.RED}✗ SYNTAX ERROR in {file_path}{self.NC}")
        print(f"  Line {error.lineno}: {error.msg}")
        if error.text:
            print(f"  {error.text.rstrip()}")
            if error.offset:
                print(f"  {' ' * (error.offset - 1)}^")
        print(
            f"\n  {self.YELLOW}Fix: Check your Python syntax at line {error.lineno}{self.NC}"
        )
        print(
            "  Common issues: missing colons, unmatched brackets, invalid indentation\n"
        )

    def report_import_errors(self, file_path: Path, errors: List[str]):
        """Report import errors with helpful formatting."""
        print(f"\n{self.RED}✗ IMPORT ERRORS in {file_path}{self.NC}")
        for error in errors:
            print(f"  {error}")
        print(
            f"\n  {self.YELLOW}Fix: Ensure all imported modules are installed or exist{self.NC}"
        )
        print("  Try: pip install <missing-module> or check module names\n")

    def report_general_error(self, file_path: Path, error: Exception):
        """Report a general error."""
        print(f"\n{self.RED}✗ ERROR validating {file_path}{self.NC}")
        print(f"  {type(error).__name__}: {error}")
        print(
            f"\n  {self.YELLOW}This might be a temporary file issue. Save again to retry.{self.NC}\n"
        )

    def report_success(self, file_path: Path):
        """Report successful validation."""
        print(f"{self.GREEN}✓ {file_path} - Valid Python code{self.NC}")

    def get_all_errors(self) -> Dict[str, List[str]]:
        """Get all current validation errors."""
        return {k: v for k, v in self.errors.items() if v}


def main():
    """Main function to run the code watchdog."""
    # Determine project root
    project_root = Path.cwd()

    # Check if we're in the LUCA project
    if not (project_root / "luca_core").exists():
        print(
            f"{CodeValidationHandler.RED}Error: Not in LUCA project root!{CodeValidationHandler.NC}"
        )
        print("Please run from /Users/dustinkirby/Documents/GitHub/luca-dev-assistant")
        sys.exit(1)

    print("🐕 LUCA Code Watchdog Started")
    print(f"Monitoring: {project_root}")
    print("Watching for Python file changes...\n")
    print("Press Ctrl+C to stop\n")

    # Create event handler and observer
    event_handler = CodeValidationHandler(project_root)
    observer = Observer()

    # Watch the entire project directory
    observer.schedule(event_handler, str(project_root), recursive=True)

    # Start the observer
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n🛑 Code Watchdog stopped")

        # Report final status
        errors = event_handler.get_all_errors()
        if errors:
            print(f"\n{event_handler.RED}Files with errors:{event_handler.NC}")
            for file_path, file_errors in errors.items():
                print(f"  - {file_path}: {len(file_errors)} error(s)")
        else:
            print(f"\n{event_handler.GREEN}All files are valid!{event_handler.NC}")

    observer.join()


if __name__ == "__main__":
    main()
