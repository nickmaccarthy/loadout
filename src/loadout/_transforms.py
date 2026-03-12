"""Frontmatter parsing and content transformation utilities."""

from __future__ import annotations

import re
from typing import Any

import yaml

from loadout.exceptions import TransformError
from loadout.models import ArtifactFrontmatter

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)---\s*\n?", re.DOTALL)


def parse_frontmatter(content: str) -> tuple[ArtifactFrontmatter, str]:
    """Parse YAML frontmatter from markdown content.

    Returns the parsed frontmatter and the remaining body content.
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return ArtifactFrontmatter(), content

    try:
        raw: dict[str, Any] = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        raise TransformError(f"Invalid YAML frontmatter: {e}") from e

    body = content[match.end() :]

    known_keys = {"description", "always_apply", "alwaysApply", "globs"}
    extra = {k: v for k, v in raw.items() if k not in known_keys}

    globs_val = raw.get("globs", [])
    if isinstance(globs_val, str):
        globs_val = [globs_val]

    fm = ArtifactFrontmatter(
        description=raw.get("description", ""),
        always_apply=raw.get("always_apply", raw.get("alwaysApply", False)),
        globs=globs_val,
        extra=extra,
    )

    return fm, body


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return content
    return content[match.end() :]


def add_cursor_frontmatter(
    content: str,
    description: str = "",
    always_apply: bool = False,
    globs: list[str] | None = None,
) -> str:
    """Add or replace frontmatter in Cursor .mdc format.

    Cursor rules require description and alwaysApply fields.
    """
    _, body = parse_frontmatter(content)

    fm_dict: dict[str, Any] = {
        "description": description,
        "alwaysApply": always_apply,
    }
    if globs:
        fm_dict["globs"] = globs

    fm_yaml = yaml.dump(fm_dict, default_flow_style=False, sort_keys=False).strip()
    return f"---\n{fm_yaml}\n---\n{body}"
