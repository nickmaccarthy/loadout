"""Claude Code adapter."""

from __future__ import annotations

from pathlib import Path

from loadout.adapters._base import _BaseFileAdapter
from loadout.models import Artifact, ArtifactType


class ClaudeCodeAdapter(_BaseFileAdapter):
    """Adapter for Claude Code (~/.claude/)."""

    @property
    def agent_name(self) -> str:
        return "claude"

    @property
    def display_name(self) -> str:
        return "Claude Code"

    @property
    def config_dir_name(self) -> str:
        return ".claude"

    def supported_artifact_types(self) -> set[ArtifactType]:
        return {ArtifactType.SKILL, ArtifactType.RULE, ArtifactType.AGENT, ArtifactType.COMMAND}

    def get_target_path(self, artifact: Artifact, config_dir: Path) -> Path:
        subdir = self._get_artifact_subdir(artifact.artifact_type)

        if artifact.artifact_type == ArtifactType.SKILL:
            # skills/<name>/ (directory)
            return config_dir / subdir / artifact.name

        if artifact.category:
            # rules/<category>/<name>.md, agents/<category>/<name>.md
            return config_dir / subdir / artifact.category / f"{artifact.name}.md"

        if artifact.artifact_type == ArtifactType.COMMAND:
            # commands/<name>.md
            return config_dir / subdir / f"{artifact.name}.md"

        return config_dir / subdir / f"{artifact.name}.md"
