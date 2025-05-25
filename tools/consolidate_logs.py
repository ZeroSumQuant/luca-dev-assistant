#!/usr/bin/env python3
"""
Consolidate and clean task logs for LUCA project.

This script:
1. Reads both task log files
2. Parses entries by date
3. Merges them in reverse chronological order (newest first)
4. Removes duplicates
5. Writes a single consolidated log file
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def parse_log_entry(content: str) -> Dict[str, List[str]]:
    """Parse log content into a dictionary of date -> entries."""
    entries: Dict[str, List[str]] = {}
    current_date = None
    current_content: List[str] = []

    lines = content.split("\n")
    date_pattern = re.compile(r"^## (\d{4}-\d{2}-\d{2})$")

    for line in lines:
        date_match = date_pattern.match(line)
        if date_match:
            # Save previous entry if exists
            if current_date and current_content:
                entries[current_date] = current_content
            # Start new entry
            current_date = date_match.group(1)
            current_content = []
        elif current_date and line.strip():  # Only add non-empty lines
            current_content.append(line)

    # Don't forget the last entry
    if current_date and current_content:
        entries[current_date] = current_content

    return entries


def merge_entries(
    entries1: Dict[str, List[str]], entries2: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """Merge two sets of entries, preferring entries2 for duplicates."""
    merged = entries1.copy()

    for date, content in entries2.items():
        if date in merged:
            # Merge content, removing duplicates
            existing = set(merged[date])
            for line in content:
                if line not in existing:
                    merged[date].append(line)
        else:
            merged[date] = content

    return merged


def format_log(entries: Dict[str, List[str]], title: str) -> str:
    """Format entries into a log file with reverse chronological order."""
    output = [f"# {title}", ""]

    # Sort dates in reverse order (newest first)
    sorted_dates = sorted(entries.keys(), reverse=True)

    for date in sorted_dates:
        output.append(f"## {date}")
        output.append("")
        output.extend(entries[date])
        output.append("")

    return "\n".join(output)


def main():
    """Main consolidation function."""
    docs_path = Path("/Users/dustinkirby/Documents/GitHub/luca-dev-assistant/docs")

    # Read both log files
    log1_path = docs_path / "task_log.md"
    log2_path = docs_path / "task_log_2025_05.md"

    print(f"Reading {log1_path}...")
    log1_content = log1_path.read_text() if log1_path.exists() else ""

    print(f"Reading {log2_path}...")
    log2_content = log2_path.read_text() if log2_path.exists() else ""

    # Parse entries
    print("Parsing entries...")
    entries1 = parse_log_entry(log1_content)
    entries2 = parse_log_entry(log2_content)

    print(f"Found {len(entries1)} dates in task_log.md")
    print(f"Found {len(entries2)} dates in task_log_2025_05.md")

    # Merge entries
    print("Merging entries...")
    merged = merge_entries(entries1, entries2)
    print(f"Total unique dates: {len(merged)}")

    # Format output
    print("Formatting consolidated log...")
    output = format_log(merged, "LUCA Dev Assistant - Task Log")

    # Write consolidated log
    output_path = docs_path / "task_log.md"
    print(f"Writing consolidated log to {output_path}...")
    output_path.write_text(output)

    # Archive the May log
    if log2_path.exists():
        archive_path = docs_path / "archive" / "task_log_2025_05.md"
        archive_path.parent.mkdir(exist_ok=True)
        print(f"Archiving {log2_path} to {archive_path}...")
        log2_path.rename(archive_path)

    print("✅ Consolidation complete!")
    print(f"   - Consolidated log: {output_path}")
    print("   - Entries are in reverse chronological order (newest first)")
    print(f"   - May log archived to: {archive_path}")


if __name__ == "__main__":
    main()
