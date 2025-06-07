#!/usr/bin/env python3
"""
Sync issue dependencies from planning document to GitHub.

This script reads dependencies from the planning document and updates
GitHub issues with appropriate labels or body text.

Usage:
    python scripts/dev-tools/sync-issue-dependencies.py [--dry-run] [--use-labels]
"""

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from typing import Dict, Set


def run_gh_command(args: list) -> str:
    """Run a GitHub CLI command and return output."""
    try:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(2)


def parse_planning_doc_dependencies(order_file: str) -> Dict[int, Set[int]]:
    """Parse dependencies from the planning document format."""
    dependencies = defaultdict(set)
    current_issue = None

    try:
        with open(order_file, "r") as f:
            for line in f:
                # Match issue headers like "- **#26** - Description"
                issue_match = re.match(r"^\s*-\s*\*\*#(\d+)\*\*", line)
                if issue_match:
                    current_issue = int(issue_match.group(1))
                    continue

                if current_issue:
                    # Match "Blocks: #60, #50, #120" pattern
                    blocks_match = re.search(r"Blocks:\s*(#\d+(?:\s*,\s*#\d+)*)", line)
                    if blocks_match:
                        blocked_issues = re.findall(r"#(\d+)", blocks_match.group(1))
                        for blocked in blocked_issues:
                            blocked_num = int(blocked)
                            dependencies[blocked_num].add(current_issue)

                    # Match "Depends on: #26" pattern
                    depends_match = re.search(
                        r"Depends on:\s*(#\d+(?:\s*,\s*#\d+)*)", line
                    )
                    if depends_match:
                        blocker_issues = re.findall(r"#(\d+)", depends_match.group(1))
                        for blocker in blocker_issues:
                            blocker_num = int(blocker)
                            dependencies[current_issue].add(blocker_num)

    except FileNotFoundError:
        print(f"Error: Planning document not found: {order_file}")
        sys.exit(1)

    return dependencies


def update_issue_body(issue_num: int, blockers: Set[int], dry_run: bool = False):
    """Update issue body to include dependency information."""
    # Get current issue body
    body_json = run_gh_command(["issue", "view", str(issue_num), "--json", "body"])
    import json

    current_body = json.loads(body_json).get("body", "") or ""

    # Check if dependencies already documented
    if any(f"Blocked by: #{b}" in current_body for b in blockers):
        print(f"  Issue #{issue_num} already has dependency info")
        return

    # Create dependency section
    dep_section = "\n\n## Dependencies\n"
    for blocker in sorted(blockers):
        dep_section += f"Blocked by: #{blocker}\n"

    # Append to body
    new_body = current_body + dep_section

    if dry_run:
        print(
            f"  Would update issue #{issue_num} with dependencies: {sorted(blockers)}"
        )
    else:
        run_gh_command(["issue", "edit", str(issue_num), "--body", new_body])
        print(f"  Updated issue #{issue_num} with dependencies: {sorted(blockers)}")


def add_issue_labels(issue_num: int, blockers: Set[int], dry_run: bool = False):
    """Add blocked-by labels to issue."""
    labels = [f"blocked-by:#{b}" for b in sorted(blockers)]

    if dry_run:
        print(f"  Would add labels to issue #{issue_num}: {labels}")
    else:
        for label in labels:
            try:
                run_gh_command(["issue", "edit", str(issue_num), "--add-label", label])
                print(f"  Added label '{label}' to issue #{issue_num}")
            except Exception as e:
                print(
                    f"  Warning: Could not add label '{label}' "
                    f"to issue #{issue_num}: {e}"
                )


def main():
    """Sync dependencies from planning doc to GitHub."""
    parser = argparse.ArgumentParser(description="Sync issue dependencies to GitHub")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    parser.add_argument(
        "--use-labels", action="store_true", help="Use labels instead of body text"
    )
    parser.add_argument(
        "--order-file",
        default="docs/development/issue-dependency-order-2025-06-07.md",
        help="Planning document with dependencies",
    )
    args = parser.parse_args()

    print("LUCA Issue Dependency Sync")
    print("=" * 50)

    # Parse dependencies
    print("Parsing planning document...")
    dependencies = parse_planning_doc_dependencies(args.order_file)

    if not dependencies:
        print("No dependencies found in planning document")
        return

    print(f"Found {len(dependencies)} issues with dependencies")
    print()

    # Update each issue
    for issue_num, blockers in sorted(dependencies.items()):
        print(f"\nProcessing issue #{issue_num}:")

        if args.use_labels:
            add_issue_labels(issue_num, blockers, dry_run=args.dry_run)
        else:
            update_issue_body(issue_num, blockers, dry_run=args.dry_run)

    print("\n✅ Sync complete!")

    if args.dry_run:
        print("\n(This was a dry run - no changes were made)")


if __name__ == "__main__":
    main()
