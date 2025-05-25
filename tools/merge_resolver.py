#!/usr/bin/env python3
"""
Quick merge conflict resolver for task logs.
Handles the common case where we have more detailed entries than main.
"""

import sys
from pathlib import Path


def resolve_task_log_conflict():
    """Resolve task log conflicts by keeping our more detailed version."""
    task_log = Path("docs/task_log.md")

    if not task_log.exists():
        print("❌ Task log not found!")
        return False

    content = task_log.read_text()

    # Check if there are conflicts
    if "<<<<<<< HEAD" not in content:
        print("✅ No conflicts in task log")
        return True

    # Split into lines for processing
    lines = content.split("\n")
    resolved = []
    in_conflict = False
    keep_head = False

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("<<<<<<< HEAD"):
            in_conflict = True
            keep_head = True
            i += 1
            continue
        elif line.startswith("======="):
            keep_head = False
            i += 1
            continue
        elif line.startswith(">>>>>>> origin/main"):
            in_conflict = False
            i += 1
            continue

        if in_conflict:
            if keep_head:
                resolved.append(line)
        else:
            resolved.append(line)

        i += 1

    # Write resolved content
    task_log.write_text("\n".join(resolved))
    print("✅ Resolved task log conflicts (kept detailed version)")
    return True


def main():
    """Main function."""
    print("🔧 Resolving merge conflicts...")

    # Resolve task log
    if not resolve_task_log_conflict():
        return 1

    # For other files, we'll handle manually
    print("\n⚠️  Other conflicts need manual resolution:")
    print("  - .coveragerc (keep our version with new exclusions)")
    print("  - requirements-dev.txt (keep both changes)")
    print("  - schemas/task_log_schema.json (keep our version)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
