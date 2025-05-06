"""
Helper module for generating more detailed changelog entries.

This simple module assists with formatting changelog entries properly
according to the Conventional Commits specification.
"""


def format_commit_message(type_str, scope, description, body=None, footer=None):
    """
    Format a commit message according to Conventional Commits specification.

    Args:
        type_str (str): The type of change (feat, fix, docs, etc.)
        scope (str): The scope of the change (optional)
        description (str): Short description of the change
        body (str, optional): Longer explanation of the change
        footer (str, optional): Information about breaking changes or
            references

    Returns:
        str: Properly formatted commit message
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
