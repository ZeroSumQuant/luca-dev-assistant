#!/usr/bin/env python3
"""Coverage tracking and badge generation for LUCA project."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


class CoverageTracker:
    """Track coverage trends and generate badges."""

    def __init__(self, history_file: str = "coverage_history.json"):
        """Initialize coverage tracker."""
        self.history_file = Path(history_file)
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        """Load coverage history from file."""
        if self.history_file.exists():
            with open(self.history_file, "r") as f:
                return json.load(f)
        return {"entries": []}

    def _save_history(self) -> None:
        """Save coverage history to file."""
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def add_coverage_entry(
        self, percentage: float, commit_sha: Optional[str] = None
    ) -> None:
        """Add a new coverage entry to history."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "percentage": percentage,
            "commit_sha": commit_sha or "unknown",
        }
        self.history["entries"].append(entry)
        self._save_history()

    def get_coverage_trend(self, last_n: int = 10) -> List[Dict]:
        """Get coverage trend for last N entries."""
        entries = self.history["entries"][-last_n:]
        return entries

    def check_coverage_regression(self, current: float) -> bool:
        """Check if current coverage is a regression."""
        if not self.history["entries"]:
            return False

        last_coverage = self.history["entries"][-1]["percentage"]
        return current < last_coverage

    def generate_badge_url(self, percentage: float) -> str:
        """Generate shields.io badge URL for coverage."""
        # Determine color based on percentage
        if percentage >= 95:
            color = "brightgreen"
        elif percentage >= 90:
            color = "green"
        elif percentage >= 80:
            color = "yellow"
        elif percentage >= 70:
            color = "orange"
        else:
            color = "red"

        # Format percentage to 2 decimal places
        formatted_pct = f"{percentage:.2f}%"

        # Generate shields.io URL
        badge_url = f"https://img.shields.io/badge/coverage-{formatted_pct}-{color}"
        return badge_url

    def update_readme_badge(self, percentage: float) -> None:
        """Update coverage badge in README.md."""
        readme_path = Path("README.md")
        if not readme_path.exists():
            print("README.md not found")
            return

        badge_url = self.generate_badge_url(percentage)
        badge_markdown = f"![Coverage]({badge_url})"

        with open(readme_path, "r") as f:
            content = f.read()

        # Replace existing coverage badge or add new one
        import re

        pattern = r"!\[Coverage\]\(https://img\.shields\.io/badge/coverage-.*?\)"

        if re.search(pattern, content):
            # Replace existing badge
            new_content = re.sub(pattern, badge_markdown, content)
        else:
            # Add badge after first heading
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    lines.insert(i + 1, f"\n{badge_markdown}\n")
                    break
            new_content = "\n".join(lines)

        with open(readme_path, "w") as f:
            f.write(new_content)

        print(f"Updated README.md with coverage badge: {percentage:.2f}%")


def main():
    """Main function for CLI usage."""
    if len(sys.argv) < 2:
        print(
            "Usage: python coverage_tracker.py <coverage_percentage> "
            "[commit_sha] [--allow-regression]"
        )
        sys.exit(1)

    try:
        coverage_pct = float(sys.argv[1])
        commit_sha = (
            sys.argv[2]
            if len(sys.argv) > 2 and not sys.argv[2].startswith("--")
            else None
        )
        allow_regression = "--allow-regression" in sys.argv

        tracker = CoverageTracker()

        # Check for regression
        if tracker.check_coverage_regression(coverage_pct) and not allow_regression:
            print(f"⚠️  Coverage regression detected! Current: {coverage_pct:.2f}%")
            last_entry = tracker.history["entries"][-1]
            print(f"Previous: {last_entry['percentage']:.2f}%")
            print("\nNote: This is expected when adding significant new code.")
            print(
                "As long as coverage stays ≥95%, the project "
                "maintains its quality standards."
            )
            print("To bypass this check, use --allow-regression flag.")
            sys.exit(1)
        elif tracker.check_coverage_regression(coverage_pct) and allow_regression:
            print(f"⚠️  Coverage regression detected! Current: {coverage_pct:.2f}%")
            last_entry = tracker.history["entries"][-1]
            print(f"Previous: {last_entry['percentage']:.2f}%")
            print("Regression allowed due to --allow-regression flag.")

        # Add entry to history
        tracker.add_coverage_entry(coverage_pct, commit_sha)

        # Update README badge
        tracker.update_readme_badge(coverage_pct)

        # Show trend
        trend = tracker.get_coverage_trend(5)
        print("\nCoverage trend (last 5 entries):")
        for entry in trend:
            print(f"  {entry['timestamp'][:10]}: {entry['percentage']:.2f}%")

        print(f"\n✅ Coverage tracking updated: {coverage_pct:.2f}%")

    except ValueError:
        print("Error: Coverage percentage must be a number")
        sys.exit(1)


if __name__ == "__main__":
    main()
