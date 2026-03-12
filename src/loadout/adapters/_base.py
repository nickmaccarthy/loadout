"""Shared base adapter with common file-copy logic."""

from __future__ import annotations

import shutil
from pathlib import Path

from loadout.adapters._protocol import AgentAdapter
from loadout.models import (
    Artifact,
    ArtifactType,
    DetectedAgent,
    InstallResult,
    InstallStatus,
)


class _BaseFileAdapter(AgentAdapter):
    """Base adapter with shared file-copy/install logic.

    Concrete adapters only need to override identity properties,
    supported types, path resolution, and transforms.
    """

    def detect(self) -> DetectedAgent | None:
        config_dir = Path.home() / self.config_dir_name
        if config_dir.is_dir():
            return DetectedAgent(
                name=self.agent_name,
                config_dir=config_dir,
                display_name=self.display_name,
            )
        return None

    def transform_content(self, artifact: Artifact, content: str) -> str:
        return content

    def transform_filename(self, artifact: Artifact, filename: str) -> str:
        return filename

    def install(
        self, artifact: Artifact, agent: DetectedAgent, force: bool = False
    ) -> InstallResult:
        if artifact.artifact_type not in self.supported_artifact_types():
            return InstallResult(
                artifact=artifact,
                agent=agent,
                status=InstallStatus.SKIPPED,
                error=(
                    f"{self.display_name} does not support"
                    f" {artifact.artifact_type.value} artifacts"
                ),
            )

        try:
            target_path = self.get_target_path(artifact, agent.config_dir)

            if target_path.exists() and not force:
                return InstallResult(
                    artifact=artifact,
                    agent=agent,
                    status=InstallStatus.ALREADY_EXISTS,
                    target_path=target_path,
                )

            target_path.parent.mkdir(parents=True, exist_ok=True)

            source = artifact.source_path
            if source.is_dir():
                return self._install_directory(artifact, agent, source, target_path, force)
            else:
                return self._install_file(artifact, agent, source, target_path)

        except Exception as e:
            return InstallResult(
                artifact=artifact,
                agent=agent,
                status=InstallStatus.FAILED,
                error=str(e),
            )

    def _install_file(
        self,
        artifact: Artifact,
        agent: DetectedAgent,
        source: Path,
        target_path: Path,
    ) -> InstallResult:
        content = source.read_text(encoding="utf-8")
        transformed = self.transform_content(artifact, content)

        final_name = self.transform_filename(artifact, target_path.name)
        final_path = target_path.parent / final_name

        final_path.write_text(transformed, encoding="utf-8")

        return InstallResult(
            artifact=artifact,
            agent=agent,
            status=InstallStatus.INSTALLED,
            target_path=final_path,
        )

    def _install_directory(
        self,
        artifact: Artifact,
        agent: DetectedAgent,
        source: Path,
        target_path: Path,
        force: bool,
    ) -> InstallResult:
        if target_path.exists() and force:
            shutil.rmtree(target_path)

        target_path.mkdir(parents=True, exist_ok=True)

        for src_file in source.rglob("*"):
            if src_file.is_file():
                rel = src_file.relative_to(source)
                dst_file = target_path / rel
                dst_file.parent.mkdir(parents=True, exist_ok=True)

                content = src_file.read_text(encoding="utf-8")
                transformed = self.transform_content(artifact, content)

                final_name = self.transform_filename(artifact, dst_file.name)
                final_path = dst_file.parent / final_name
                final_path.write_text(transformed, encoding="utf-8")

        return InstallResult(
            artifact=artifact,
            agent=agent,
            status=InstallStatus.INSTALLED,
            target_path=target_path,
        )

    def _get_artifact_subdir(self, artifact_type: ArtifactType) -> str:
        """Map artifact type to subdirectory name."""
        return {
            ArtifactType.SKILL: "skills",
            ArtifactType.RULE: "rules",
            ArtifactType.AGENT: "agents",
            ArtifactType.COMMAND: "commands",
        }[artifact_type]
