"""Shared base adapter with common file-copy logic."""

from __future__ import annotations

import shutil
from pathlib import Path

from loadout._hashing import hash_content, hash_directory, hash_file
from loadout.adapters._protocol import AgentAdapter
from loadout.models import (
    Artifact,
    ArtifactType,
    CheckResult,
    CheckStatus,
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
        final_name = self.transform_filename(artifact, target_path.name)
        final_path = target_path.parent / final_name
        self._copy_file(source, final_path, artifact)

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

                final_name = self.transform_filename(artifact, dst_file.name)
                final_path = dst_file.parent / final_name
                self._copy_file(src_file, final_path, artifact)

        return InstallResult(
            artifact=artifact,
            agent=agent,
            status=InstallStatus.INSTALLED,
            target_path=target_path,
        )

    def check(self, artifact: Artifact, agent: DetectedAgent) -> CheckResult:
        if artifact.artifact_type not in self.supported_artifact_types():
            return CheckResult(
                artifact=artifact,
                agent=agent,
                status=CheckStatus.UNKNOWN,
            )

        try:
            target_path = self.get_target_path(artifact, agent.config_dir)

            if not target_path.exists():
                return CheckResult(
                    artifact=artifact,
                    agent=agent,
                    status=CheckStatus.MISSING,
                    target_path=target_path,
                )

            source = artifact.source_path
            if source.is_dir():
                source_hash = self._hash_source_directory(artifact, source)
                installed_hash = hash_directory(target_path)
            else:
                source_hash = self._hash_source_file(artifact, source)
                final_name = self.transform_filename(artifact, target_path.name)
                final_path = target_path.parent / final_name
                if not final_path.exists():
                    return CheckResult(
                        artifact=artifact,
                        agent=agent,
                        status=CheckStatus.MISSING,
                        target_path=final_path,
                    )
                installed_hash = hash_file(final_path)

            status = CheckStatus.CURRENT if source_hash == installed_hash else CheckStatus.STALE

            return CheckResult(
                artifact=artifact,
                agent=agent,
                status=status,
                source_hash=source_hash,
                installed_hash=installed_hash,
                target_path=target_path,
            )
        except Exception:
            return CheckResult(
                artifact=artifact,
                agent=agent,
                status=CheckStatus.UNKNOWN,
                target_path=target_path if "target_path" in dir() else None,
            )

    def _hash_source_file(self, artifact: Artifact, source: Path) -> str:
        """Hash a source file after applying content and filename transforms."""
        content = source.read_text(encoding="utf-8")
        transformed = self.transform_content(artifact, content)
        return hash_content(transformed)

    def _hash_source_directory(self, artifact: Artifact, source: Path) -> str:
        """Hash a source directory after applying transforms to each file."""
        import hashlib as _hashlib

        file_hashes: list[str] = []
        for f in sorted(source.rglob("*")):
            if f.is_file():
                rel = f.relative_to(source)
                final_name = self.transform_filename(artifact, f.name)
                rel_transformed = rel.parent / final_name

                try:
                    content = f.read_text(encoding="utf-8")
                    transformed = self.transform_content(artifact, content)
                    h = hash_content(transformed)
                except UnicodeDecodeError:
                    h = hash_file(f)

                file_hashes.append(f"{rel_transformed}:{h}")

        combined = "\n".join(file_hashes)
        return _hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def _get_artifact_subdir(self, artifact_type: ArtifactType) -> str:
        """Map artifact type to subdirectory name."""
        return {
            ArtifactType.SKILL: "skills",
            ArtifactType.RULE: "rules",
            ArtifactType.AGENT: "agents",
            ArtifactType.COMMAND: "commands",
        }[artifact_type]

    def _copy_file(self, source: Path, destination: Path, artifact: Artifact) -> None:
        """Copy a file, transforming UTF-8 text while preserving binary files."""
        try:
            content = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(source, destination)
            return

        transformed = self.transform_content(artifact, content)
        destination.write_text(transformed, encoding="utf-8")
        shutil.copystat(source, destination)
