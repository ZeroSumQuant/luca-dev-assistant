#!/usr/bin/env python3
"""
Validate GitHub issue dependencies and ordering.

This script checks:
1. No issue is blocked by another issue scheduled after it
2. No blocker appears after its dependents
3. No circular dependencies exist
4. High priority issues are appropriately positioned

Usage:
    python scripts/dev-tools/validate-issue-order.py [--verbose] [--dry-run]

Exit codes:
    0 = all clear
    1 = validation warnings (priority misplaced)
    2 = hard errors (cycle, dependency order violation)
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from typing import Dict, List, Set


def run_gh_command(args: List[str]) -> str:
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


def get_all_issues(verbose: bool = False) -> List[Dict]:
    """Fetch all open issues with their metadata."""
    if verbose:
        print("Fetching all open issues...")
    output = run_gh_command(
        [
            "issue",
            "list",
            "--state",
            "open",
            "--limit",
            "200",
            "--json",
            "number,title,labels,body",
        ]
    )
    return json.loads(output)


def validate_issue_exists(
    issue_num: int, all_issue_numbers: Set[int], source: str
) -> bool:
    """Validate that a referenced issue exists."""
    if issue_num not in all_issue_numbers:
        print(f"❌ ERROR: Issue #{issue_num} referenced in {source} does not exist!")
        return False
    return True


def extract_dependencies(
    issues: List[Dict], verbose: bool = False
) -> Dict[int, Set[int]]:
    """Extract blocked-by relationships from multiple sources."""
    dependencies = defaultdict(set)
    all_issue_numbers = {issue["number"] for issue in issues}
    has_errors = False

    for issue in issues:
        issue_num = issue["number"]

        # Source 1: Labels (blocked-by:#nn)
        for label in issue.get("labels", []):
            label_name = label["name"]
            if label_name.startswith("blocked-by:#"):
                try:
                    blocker = int(label_name.split("#")[1])
                    if validate_issue_exists(
                        blocker, all_issue_numbers, f"label on #{issue_num}"
                    ):
                        dependencies[issue_num].add(blocker)
                        if verbose:
                            print(
                                f"  Found dependency: #{issue_num} blocked by "
                                f"#{blocker} (via label)"
                            )
                    else:
                        has_errors = True
                except (ValueError, IndexError):
                    print(f"Warning: Invalid blocked-by label: {label_name}")

        # Source 2: Issue body patterns
        body = issue.get("body", "") or ""

        # Pattern: "Blocked by: #123" or "Blocked-by: #123" or "Depends on: #123"
        # Using single comprehensive pattern to avoid double-counting
        dependency_pattern = r"(?:Blocked[-\s]by|Depends[-\s]on):\s*#(\d+)"
        matches = re.findall(dependency_pattern, body, re.IGNORECASE)
        for match in matches:
            blocker = int(match)
            if validate_issue_exists(
                blocker, all_issue_numbers, f"body of #{issue_num}"
            ):
                dependencies[issue_num].add(blocker)
                if verbose:
                    print(
                        f"  Found dependency: #{issue_num} blocked by "
                        f"#{blocker} (via body text)"
                    )
            else:
                has_errors = True

    # Source 3: GitHub's built-in linkedIssues
    # TODO: Implement GraphQL query for:
    # timelineItems(first: 100, itemTypes: [CONNECTED_EVENT])
    # This would capture dependencies created through GitHub's UI
    # Requires authenticated GraphQL API access

    if has_errors:
        print("❌ Found references to non-existent issues!")
        sys.exit(2)

    return dependencies


def detect_cycles(dependencies: Dict[int, Set[int]]) -> List[List[int]]:
    """Detect circular dependencies using DFS."""

    def dfs(node: int, path: List[int], visited: Set[int]) -> List[List[int]]:
        if node in path:
            cycle_start = path.index(node)
            return [path[cycle_start:] + [node]]

        if node in visited:
            return []

        visited.add(node)
        path.append(node)

        cycles = []
        for dep in dependencies.get(node, []):
            cycles.extend(dfs(dep, path.copy(), visited))

        return cycles

    all_cycles = []
    visited: Set[int] = set()

    for issue in dependencies:
        if issue not in visited:
            cycles = dfs(issue, [], visited)
            all_cycles.extend(cycles)

    return all_cycles


def get_issue_order(order_file: str) -> List[int]:
    """Read the defined issue order from our documentation."""
    order = []

    try:
        with open(order_file, "r") as f:
            content = f.read()

        # Extract issue numbers from the markdown
        pattern = r"\*\*#(\d+)\*\*"
        matches = re.findall(pattern, content)
        order = [int(num) for num in matches]

    except FileNotFoundError:
        print(f"Error: Issue order documentation not found at {order_file}")
        sys.exit(2)

    return order


def validate_order(
    issues: List[Dict], dependencies: Dict[int, Set[int]], order: List[int]
) -> List[str]:
    """Validate that the order respects dependencies."""
    violations = []

    # Create position map
    position = {num: idx for idx, num in enumerate(order)}

    # Check each dependency
    for issue_num, blockers in dependencies.items():
        if issue_num not in position:
            continue

        issue_pos = position[issue_num]

        for blocker in blockers:
            if blocker not in position:
                violations.append(
                    f"Issue #{issue_num} depends on #{blocker} "
                    f"which is not in the order"
                )
                continue

            blocker_pos = position[blocker]

            if blocker_pos > issue_pos:
                violations.append(
                    f"Issue #{issue_num} (position {issue_pos}) is blocked by "
                    f"#{blocker} (position {blocker_pos}) which comes after it"
                )

    return violations


def check_priority_placement(issues: List[Dict], order: List[int]) -> List[str]:
    """Check if high priority issues are appropriately placed."""
    warnings = []

    # Get high priority issues
    high_priority = []
    for issue in issues:
        for label in issue.get("labels", []):
            if label["name"] in ["P0-critical", "P1-high"]:
                high_priority.append(issue["number"])
                break

    # Check their positions
    position = {num: idx for idx, num in enumerate(order)}

    high_priority_positions = []
    for issue_num in high_priority:
        if issue_num in position:
            pos = position[issue_num]
            high_priority_positions.append((issue_num, pos))

    # Sort by position
    high_priority_positions.sort(key=lambda x: x[1])

    # Report if any high priority issues are beyond position 10
    for issue_num, pos in high_priority_positions:
        if pos > 10:
            warnings.append(
                f"High priority issue #{issue_num} is at position {pos} "
                f"(consider moving earlier unless blocked by dependencies)"
            )

    return warnings


def main():
    """Run all validation checks."""
    parser = argparse.ArgumentParser(description="Validate GitHub issue dependencies")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--dry-run", action="store_true", help="Run checks but don't alter exit code"
    )
    parser.add_argument(
        "--order-file",
        default="docs/development/issue-dependency-order-2025-06-07.md",
        help="Markdown file that defines ordered issue list",
    )
    args = parser.parse_args()

    print("LUCA Issue Dependency Validator")
    print("=" * 50)

    # Get data
    issues = get_all_issues(verbose=args.verbose)
    dependencies = extract_dependencies(issues, verbose=args.verbose)
    order = get_issue_order(args.order_file)

    if not order:
        print("Error: Could not load issue order")
        sys.exit(2)

    print(f"Found {len(issues)} open issues")
    print(f"Found {len(dependencies)} issues with dependencies")
    print(f"Loaded order with {len(order)} issues")
    print()

    # Track errors and warnings
    has_errors = False
    has_warnings = False

    # Check for cycles
    print("Checking for circular dependencies...")
    cycles = detect_cycles(dependencies)
    if cycles:
        has_errors = True
        print("❌ CIRCULAR DEPENDENCIES DETECTED:")
        for cycle in cycles:
            print(f"   Cycle: {' → '.join(map(str, cycle))}")
    else:
        print("✅ No circular dependencies found")
    print()

    # Validate order
    print("Validating issue order...")
    violations = validate_order(issues, dependencies, order)
    if violations:
        has_errors = True
        print("❌ DEPENDENCY VIOLATIONS:")
        for violation in violations:
            print(f"   {violation}")
    else:
        print("✅ All dependencies are properly ordered")
    print()

    # Check priority placement
    print("Checking priority placement...")
    warnings = check_priority_placement(issues, order)
    if warnings:
        has_warnings = True
        print("⚠️  PRIORITY WARNINGS:")
        for warning in warnings:
            print(f"   {warning}")
    else:
        print("✅ All high priority issues are well-positioned")
    print()

    # Summary and exit with proper exit code logic
    exit_code = 2 if has_errors else 1 if has_warnings else 0

    if exit_code == 0:
        print("✅ All validation checks passed!")
    elif exit_code == 1:
        print("⚠️  Found warnings that should be reviewed")
    else:
        print("❌ Found hard errors that must be fixed!")

    if args.dry_run:
        print("\n(Dry-run – exit code suppressed)")
        exit_code = 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
