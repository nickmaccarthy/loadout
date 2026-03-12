"""Cursor adapter with .mdc format transformation."""

from __future__ import annotations

from pathlib import Path

from loadout._transforms import add_cursor_frontmatter, parse_frontmatter
from loadout.adapters._base import _BaseFileAdapter
from loadout.models import Artifact, ArtifactType


class CursorAdapter(_BaseFileAdapter):
    """Adapter for Cursor (~/.cursor/).

    Cursor rules use .mdc format with description/alwaysApply frontmatter.
    Skills are installed as-is.
    """

    @property
    def agent_name(self) -> str:
        return "cursor"

    @property
    def display_name(self) -> str:
        return "Cursor"

    @property
    def config_dir_name(self) -> str:
        return ".cursor"

    def supported_artifact_types(self) -> set[ArtifactType]:
        return {ArtifactType.SKILL, ArtifactType.RULE}

    def get_target_path(self, artifact: Artifact, config_dir: Path) -> Path:
        subdir = self._get_artifact_subdir(artifact.artifact_type)

        if artifact.artifact_type == ArtifactType.SKILL:
            return config_dir / subdir / artifact.name

        if artifact.category:
            return config_dir / subdir / artifact.category / f"{artifact.name}.mdc"

        return config_dir / subdir / f"{artifact.name}.mdc"

    def transform_content(self, artifact: Artifact, content: str) -> str:
        if artifact.artifact_type != ArtifactType.RULE:
            return content

        fm, _ = parse_frontmatter(content)
        return add_cursor_frontmatter(
            content,
            description=fm.description,
            always_apply=fm.always_apply,
            globs=fm.globs if fm.globs else None,
        )

    def transform_filename(self, artifact: Artifact, filename: str) -> str:
        if artifact.artifact_type == ArtifactType.RULE and filename.endswith(".md"):
            return filename[:-3] + ".mdc"
        return filename
