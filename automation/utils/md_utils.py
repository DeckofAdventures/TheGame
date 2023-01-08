def make_bullet(value, indents=0):
    """Return string with 4 spaces per indent, plus `- `"""
    spaces = indents * "    "
    return f"{spaces}- {value}\n"


def make_link(value: str, indents: int = 0) -> str:
    """Make relative within-doc bulleted link for TOC. [name](#no-spaces)

    Args:
        value (str): heading name
        indents (int): indent level for heading

    Returns:
        link (str): markdown formatted indented bullet with relative path for
            table of contents. E.g., `    - [Heading name](#heading-name)`
    """
    no_spaces = value.lower().replace(" ", "-")
    link = f"[{value}](#{no_spaces})"
    return make_bullet(link, indents)


def make_header(value: str, level: (int) = 0):
    """Return string with level+1 * `#`

    Args:
        value (str): heading content
        level (int): heading level. e.g., `# Zero`, `## One`
    """
    prefix = level * "#"
    return f"\n#{prefix} {value}\n"
