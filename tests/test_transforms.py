"""Tests for frontmatter parsing and content transforms."""

import pytest

from loadout._transforms import add_cursor_frontmatter, parse_frontmatter, strip_frontmatter
from loadout.exceptions import TransformError


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        content = "---\ndescription: Test\nalways_apply: true\n---\n# Body\n"
        fm, body = parse_frontmatter(content)
        assert fm.description == "Test"
        assert fm.always_apply is True
        assert body == "# Body\n"

    def test_camel_case_always_apply(self):
        content = "---\ndescription: Test\nalwaysApply: true\n---\n# Body\n"
        fm, body = parse_frontmatter(content)
        assert fm.always_apply is True

    def test_globs_as_string(self):
        content = "---\nglobs: '*.py'\n---\n# Body\n"
        fm, _ = parse_frontmatter(content)
        assert fm.globs == ["*.py"]

    def test_globs_as_list(self):
        content = "---\nglobs:\n  - '*.py'\n  - '*.js'\n---\n# Body\n"
        fm, _ = parse_frontmatter(content)
        assert fm.globs == ["*.py", "*.js"]

    def test_no_frontmatter(self):
        content = "# Just a heading\nSome content.\n"
        fm, body = parse_frontmatter(content)
        assert fm.description == ""
        assert body == content

    def test_extra_fields(self):
        content = "---\ndescription: Test\ncustom_field: value\n---\n# Body\n"
        fm, _ = parse_frontmatter(content)
        assert fm.extra == {"custom_field": "value"}

    def test_invalid_yaml(self):
        content = "---\n: invalid yaml [\n---\n# Body\n"
        with pytest.raises(TransformError, match="Invalid YAML"):
            parse_frontmatter(content)

    def test_empty_frontmatter(self):
        content = "---\n---\n# Body\n"
        fm, body = parse_frontmatter(content)
        assert fm.description == ""
        assert body == "# Body\n"


class TestStripFrontmatter:
    def test_strips(self):
        content = "---\ndescription: Test\n---\n# Body\n"
        assert strip_frontmatter(content) == "# Body\n"

    def test_no_frontmatter(self):
        content = "# Just a heading\n"
        assert strip_frontmatter(content) == content


class TestAddCursorFrontmatter:
    def test_adds_frontmatter(self):
        content = "# My Rule\nDo the thing.\n"
        result = add_cursor_frontmatter(content, description="My Rule", always_apply=True)
        assert "description: My Rule" in result
        assert "alwaysApply: true" in result
        assert "# My Rule\nDo the thing.\n" in result

    def test_replaces_existing_frontmatter(self):
        content = "---\nold: value\n---\n# Body\n"
        result = add_cursor_frontmatter(content, description="New")
        assert "old: value" not in result
        assert "description: New" in result
        assert "# Body\n" in result

    def test_with_globs(self):
        content = "# Rule\n"
        result = add_cursor_frontmatter(
            content, description="Test", globs=["*.py", "*.js"]
        )
        assert "globs:" in result
        assert "*.py" in result
