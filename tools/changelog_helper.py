"""
Helper module for generating more detailed changelog entries.

This simple module assists with formatting changelog entries properly
according to the Conventional Commits specification.
"""

from typing import Optional


def format_commit_message(
    type_str: str,
    scope: Optional[str],
    description: str,
    body: Optional[str] = None,
    footer: Optional[str] = None,
) -> str:
    """
    Format a commit message according to Conventional Commits specification.

    Args:
        type_str: The type of change (feat, fix, docs, etc.)
        scope: The scope of the change (optional, can be None)
        description: Short description of the change
        body: Longer explanation of the change (optional)
        footer: Information about breaking changes or references (optional)

    Returns:
        Properly formatted commit message as a string
    """
    if scope:
        header = f"{type_str}({scope}): {description}"
    else:
        header = f"{type_str}: {description}"

    if not body and not footer:
        return header

    message = header + "\n\n"

    if body:
        message += body + "\n\n"

    if footer:
        message += footer

    return message
