#!/usr/bin/env python3
"""
Claude Omniscience Script - Everything Claude needs to know in one command
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Optional imports
try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class ClaudeOmniscience:
    """Gathers complete project context for Claude"""

    def __init__(self, root_path: Optional[Path] = None):
        self.root_path = root_path or Path.cwd()
        self.cache: Dict[str, str] = {}
        self.token_encoder = None
        if TIKTOKEN_AVAILABLE:
            try:
                self.token_encoder = tiktoken.encoding_for_model("gpt-4")
            except Exception:
                self.token_encoder = tiktoken.get_encoding("cl100k_base")

    def run_command(
        self, cmd: List[str], cwd: Optional[Path] = None
    ) -> Tuple[str, int]:
        """Run a command and return output + return code"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd or self.root_path,
                timeout=5,
            )
            return result.stdout.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "Command timed out", 1
        except Exception as e:
            return f"Error: {e}", 1

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.token_encoder:
            return len(self.token_encoder.encode(text))
        # Rough estimate if tiktoken not available
        return len(text) // 4

    def get_location_and_state(self) -> Dict[str, Any]:
        """Get project location and basic state"""
        # Count files
        py_files = list(self.root_path.rglob("*.py"))
        total_files = len(list(self.root_path.rglob("*")))

        # Get git branch
        branch, _ = self.run_command(["git", "branch", "--show-current"])

        return {
            "root": str(self.root_path),
            "branch": branch or "unknown",
            "python_files": len(py_files),
            "total_files": total_files,
            "size_mb": sum(
                f.stat().st_size for f in self.root_path.rglob("*") if f.is_file()
            )
            / 1024
            / 1024,
        }

    def get_git_status(self) -> Dict[str, Any]:
        """Get current git status"""
        status, _ = self.run_command(["git", "status", "--porcelain"])

        staged = []
        unstaged = []
        untracked = []

        for line in status.split("\n"):
            if not line:
                continue
            status_code = line[:2]
            filename = line[3:]

            if status_code[0] in ["A", "M", "D", "R"]:
                staged.append(filename)
            if status_code[1] in ["M", "D"]:
                unstaged.append(filename)
            if status_code == "??":
                untracked.append(filename)

        # Get recent commits
        commits, _ = self.run_command(
            ["git", "log", "--oneline", "-5", "--pretty=format:%h %s"]
        )

        return {
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked,
            "recent_commits": commits.split("\n") if commits else [],
        }

    def get_recent_activity(self, hours: int = 2) -> List[str]:
        """Get files modified in the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_files = []

        for path in self.root_path.rglob("*.py"):
            if path.is_file():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime > cutoff:
                    recent_files.append((path.relative_to(self.root_path), mtime))

        # Sort by modification time
        recent_files.sort(key=lambda x: x[1], reverse=True)
        return [str(f[0]) for f in recent_files[:10]]

    def get_test_status(self) -> Dict[str, Any]:
        """Get test status without running them"""
        # Check if tests exist
        test_dir = self.root_path / "tests"
        if not test_dir.exists():
            return {"status": "no_tests", "message": "No tests directory found"}

        # Try to get last test run from pytest cache
        cache_dir = self.root_path / ".pytest_cache"
        if cache_dir.exists():
            lastfailed = cache_dir / "v" / "cache" / "lastfailed"
            if lastfailed.exists():
                try:
                    with open(lastfailed) as f:
                        failed = json.load(f)
                        if failed:
                            return {
                                "status": "failing",
                                "failed_count": len(failed),
                                "failed_tests": list(failed.keys())[:5],
                            }
                        else:
                            return {
                                "status": "passing",
                                "message": "All tests passed (cached)",
                            }
                except Exception:
                    pass

        # Count test files
        test_files = list(test_dir.rglob("test_*.py"))
        return {
            "status": "unknown",
            "test_files": len(test_files),
            "message": "Run pytest to update status",
        }

    def find_errors_and_issues(self) -> Dict[str, List[str]]:
        """Find syntax errors, TODOs, and other issues"""
        issues: Dict[str, List[str]] = {
            "syntax_errors": [],
            "todos": [],
            "fixmes": [],
            "type_errors": [],
        }

        for py_file in self.root_path.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            # Check for syntax errors
            result, code = self.run_command(
                ["python3", "-m", "py_compile", str(py_file)]
            )
            if code != 0:
                issues["syntax_errors"].append(str(py_file.relative_to(self.root_path)))

            # Check for TODOs and FIXMEs
            try:
                with open(py_file, "r") as f:
                    for i, line in enumerate(f, 1):
                        if "TODO" in line:
                            issues["todos"].append(
                                f"{py_file.relative_to(self.root_path)}:{i}"
                            )
                        if "FIXME" in line:
                            issues["fixmes"].append(
                                f"{py_file.relative_to(self.root_path)}:{i}"
                            )
            except Exception:
                pass

        return issues

    def get_environment_info(self) -> Dict[str, Any]:
        """Get Python environment information"""
        python_version, _ = self.run_command([sys.executable, "--version"])

        # Check if in virtual environment
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

        # Get key packages
        packages = {}
        for pkg in ["streamlit", "pytest", "black", "mypy", "tiktoken"]:
            _, code = self.run_command([sys.executable, "-m", pkg, "--version"])
            packages[pkg] = "installed" if code == 0 else "not installed"

        return {
            "python_version": python_version,
            "in_virtualenv": in_venv,
            "venv_path": os.environ.get("VIRTUAL_ENV", "N/A"),
            "key_packages": packages,
        }

    def suggest_next_steps(self, context: Dict) -> List[str]:
        """Suggest next steps based on current state"""
        suggestions = []

        # Check git status
        if context["git_status"]["unstaged"]:
            suggestions.append("Stage and commit your changes")

        # Check test status
        if context["test_status"]["status"] == "failing":
            suggestions.append(
                f"Fix {context['test_status']['failed_count']} failing tests"
            )
        elif context["test_status"]["status"] == "unknown":
            suggestions.append("Run pytest to check test status")

        # Check for issues
        if context["errors"]["syntax_errors"]:
            suggestions.append(
                f"Fix syntax errors in {len(context['errors']['syntax_errors'])} files"
            )

        if context["errors"]["todos"]:
            suggestions.append(f"Address {len(context['errors']['todos'])} TODO items")

        # Check environment
        if not context["environment"]["in_virtualenv"]:
            suggestions.append("Activate virtual environment")

        return suggestions[:5]  # Top 5 suggestions

    def gather_everything(self, minimal: bool = False, verbose: bool = False) -> str:
        """Gather all context information"""
        output = []

        # Header
        output.append("🧠 CLAUDE OMNISCIENCE OUTPUT")
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("=" * 50)
        output.append("")

        # Gather all information
        location = self.get_location_and_state()
        git_status = self.get_git_status()
        recent = self.get_recent_activity()
        tests = self.get_test_status()
        errors = self.find_errors_and_issues()
        env = self.get_environment_info()

        context = {
            "location": location,
            "git_status": git_status,
            "recent_activity": recent,
            "test_status": tests,
            "errors": errors,
            "environment": env,
        }

        suggestions = self.suggest_next_steps(context)

        # Format output
        output.append("📍 LOCATION & STATE")
        output.append(f"• Root: {location['root']}")
        output.append(f"• Branch: {location['branch']}")
        output.append(
            f"• Files: {location['python_files']} Python, {location['total_files']} total"
        )
        output.append(f"• Size: {location['size_mb']:.1f} MB")
        output.append("")

        output.append("🔄 CURRENT REALITY")
        output.append(f"• Staged: {len(git_status['staged'])} files")
        output.append(f"• Unstaged: {len(git_status['unstaged'])} files")
        output.append(f"• Untracked: {len(git_status['untracked'])} files")
        if git_status["recent_commits"]:
            output.append("• Recent commits:")
            for commit in git_status["recent_commits"][:3]:
                output.append(f"  - {commit}")
        output.append("")

        if not minimal:
            output.append("📝 RECENT ACTIVITY (last 2 hours)")
            if recent:
                for file in recent[:5]:
                    output.append(f"• {file}")
            else:
                output.append("• No recent changes")
            output.append("")

        output.append("🧪 TEST STATUS")
        if tests["status"] == "passing":
            output.append("• ✅ All tests passing")
        elif tests["status"] == "failing":
            output.append(f"• ❌ {tests['failed_count']} tests failing")
            if verbose and "failed_tests" in tests:
                for test in tests["failed_tests"][:3]:
                    output.append(f"  - {test}")
        else:
            output.append(f"• ❓ {tests.get('message', 'Unknown status')}")
        output.append("")

        if errors["syntax_errors"] or errors["todos"] or errors["fixmes"]:
            output.append("🔥 ERRORS & ISSUES")
            if errors["syntax_errors"]:
                output.append(f"• Syntax errors: {len(errors['syntax_errors'])} files")
            if errors["todos"]:
                output.append(f"• TODOs: {len(errors['todos'])} items")
            if errors["fixmes"]:
                output.append(f"• FIXMEs: {len(errors['fixmes'])} items")
            output.append("")

        if not minimal:
            output.append("🔧 ENVIRONMENT")
            output.append(f"• Python: {env['python_version']}")
            output.append(
                f"• Virtual env: {'✅ Active' if env['in_virtualenv'] else '❌ Not active'}"
            )
            if verbose:
                output.append("• Key packages:")
                for pkg, status in env["key_packages"].items():
                    output.append(f"  - {pkg}: {status}")
            output.append("")

        if suggestions:
            output.append("🎯 NEXT STEPS")
            for i, suggestion in enumerate(suggestions, 1):
                output.append(f"{i}. {suggestion}")
            output.append("")

        # Token statistics
        full_output = "\n".join(output)
        if TIKTOKEN_AVAILABLE and not minimal:
            tokens = self.count_tokens(full_output)
            output.append("=" * 50)
            output.append(f"📊 Token count: {tokens} tokens")
            output.append(f"💰 Estimated savings: ~{650 - tokens} tokens vs Q&A")

        return "\n".join(output)


class OmniscienceWatcher(FileSystemEventHandler):
    """Watch for file changes and update omniscience"""

    def __init__(self, omniscience: ClaudeOmniscience):
        self.omniscience = omniscience
        self.last_update = time.time()

    def on_modified(self, event):
        if event.is_directory:
            return

        # Debounce - only update every 2 seconds
        if time.time() - self.last_update < 2:
            return

        self.last_update = time.time()
        print(
            f"\n[{datetime.now().strftime('%H:%M:%S')}] Change detected: {event.src_path}"
        )
        print("Updating omniscience...\n")
        print(self.omniscience.gather_everything(minimal=True))


# Registry lives in its own module now
from omn_plugins import run_all_plugins


def main():
    # Import plugins to register them
    try:
        import fingerprint  # noqa
    except ImportError:
        pass

    parser = argparse.ArgumentParser(
        description="Claude Omniscience - Everything Claude needs to know"
    )
    parser.add_argument(
        "--watch", "-w", action="store_true", help="Watch mode - live updates"
    )
    parser.add_argument("--minimal", "-m", action="store_true", help="Minimal output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--no-tokens", action="store_true", help="Disable token counting"
    )
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument(
        "--deep",
        action="store_true",
        help="Run registered deep-analysis plugins (fingerprint, import graph, etc.)",
    )

    args = parser.parse_args()

    # Check if we're in a git repository
    if not (Path.cwd() / ".git").exists():
        print("❌ Error: Not in a git repository!")
        print("Please run this from your project root.")
        sys.exit(1)

    omniscience = ClaudeOmniscience()

    if args.watch:
        if not WATCHDOG_AVAILABLE:
            print("❌ Watch mode requires watchdog: pip install watchdog")
            sys.exit(1)

        print("👁️  Starting omniscience watch mode...")
        print("Press Ctrl+C to stop\n")

        # Print initial state
        print(omniscience.gather_everything(minimal=args.minimal, verbose=args.verbose))

        # Start watching
        event_handler = OmniscienceWatcher(omniscience)
        observer = Observer()
        observer.schedule(event_handler, str(Path.cwd()), recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        # Single run
        output = omniscience.gather_everything(
            minimal=args.minimal, verbose=args.verbose
        )
        print(output)

        # Deep analysis (optional)
        if args.deep:
            print("\n" + run_all_plugins())

        # Save token statistics
        if TIKTOKEN_AVAILABLE and not args.no_tokens:
            stats_file = Path.home() / ".luca" / "token_stats.json"
            stats_file.parent.mkdir(exist_ok=True)

            try:
                if stats_file.exists():
                    with open(stats_file) as f:
                        stats = json.load(f)
                else:
                    stats = {"runs": 0, "total_tokens_used": 0, "total_tokens_saved": 0}

                tokens = omniscience.count_tokens(output)
                stats["runs"] += 1
                stats["total_tokens_used"] += tokens
                stats["total_tokens_saved"] += max(0, 650 - tokens)
                stats["efficiency"] = (
                    stats["total_tokens_saved"] / stats["total_tokens_used"]
                ) * 100

                with open(stats_file, "w") as f:
                    json.dump(stats, f, indent=2)
            except Exception:
                pass  # Don't fail on stats errors


if __name__ == "__main__":
    main()
