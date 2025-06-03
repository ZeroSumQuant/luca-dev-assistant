import json
import os
import pathlib
import sys
import textwrap

issues = json.load(open("OPEN_ISSUES.json"))
lines = ["| # | Title | Labels | Assignees |", "|---|-------|--------|-----------|"]
for it in issues:
    labels = ", ".join(label["name"] for label in it["labels"]) or "—"
    assignees = ", ".join(a["login"] for a in it["assignees"]) or "—"
    title = textwrap.shorten(it["title"], width=60, placeholder="…")
    lines.append(f"| {it['number']} | {title} | {labels} | {assignees} |")
pathlib.Path("OPEN_ISSUES.md").write_text("\n".join(lines))
