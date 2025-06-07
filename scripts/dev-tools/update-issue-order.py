#!/usr/bin/env python3
"""
Update GitHub issue titles with order numbers.
"""

import subprocess

# The order from our planning document
issue_order = [
    26,
    60,
    27,
    56,
    55,
    54,
    50,
    51,
    82,
    83,
    84,
    30,
    96,
    29,
    59,
    120,
    58,
    57,
    107,
    108,
    109,
    110,
    119,
    62,
    115,
    63,
    65,
    31,
    32,
]


def run_gh_command(args):
    """Run a GitHub CLI command."""
    try:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


def main():
    """Update issue titles with order numbers."""
    print("Updating GitHub issue titles with order numbers...")

    for position, issue_num in enumerate(issue_order, 1):
        # Get current title
        result = run_gh_command(["issue", "view", str(issue_num), "--json", "title"])
        if not result:
            continue

        import json

        current_title = json.loads(result)["title"]

        # Remove any existing order prefix
        if current_title.startswith("[") and "]" in current_title:
            current_title = current_title.split("]", 1)[1].strip()

        # Add new order prefix
        new_title = f"[{position:02d}] {current_title}"

        # Update the issue
        print(f"Updating #{issue_num}: {new_title}")
        run_gh_command(["issue", "edit", str(issue_num), "--title", new_title])

    print("\n✅ Issue titles updated with order numbers!")
    print("\nNow issues will appear in order when sorted by title!")


if __name__ == "__main__":
    main()
