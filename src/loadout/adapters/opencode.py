"""OpenCode adapter."""

from __future__ import annotations

from pathlib import Path

from loadout.adapters._base import _BaseFileAdapter
from loadout.models import Artifact, ArtifactType


class OpenCodeAdapter(_BaseFileAdapter):
    """Adapter for OpenCode (~/.opencode/)."""

    @property
    def agent_name(self) -> str:
        return "opencode"

    @property
    def display_name(self) -> str:
        return "OpenCode"

    @property
    def config_dir_name(self) -> str:
        return ".opencode"

    def supported_artifact_types(self) -> set[ArtifactType]:
        return {ArtifactType.SKILL, ArtifactType.COMMAND}

    def get_target_path(self, artifact: Artifact, config_dir: Path) -> Path:
        subdir = self._get_artifact_subdir(artifact.artifact_type)

        if artifact.artifact_type == ArtifactType.SKILL:
            return config_dir / subdir / artifact.name

        # commands/<name>.md
        return config_dir / subdir / f"{artifact.name}.md"
