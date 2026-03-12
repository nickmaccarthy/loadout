"""Tests for the OpenCode adapter."""

from pathlib import Path
from unittest.mock import patch

from loadout.adapters.opencode import OpenCodeAdapter
from loadout.models import (
    Artifact,
    ArtifactFrontmatter,
    ArtifactType,
    DetectedAgent,
    InstallStatus,
)


class TestOpenCodeAdapter:
    def setup_method(self):
        self.adapter = OpenCodeAdapter()

    def test_properties(self):
        assert self.adapter.agent_name == "opencode"
        assert self.adapter.display_name == "OpenCode"
        assert self.adapter.config_dir_name == ".opencode"

    def test_supported_types(self):
        types = self.adapter.supported_artifact_types()
        assert ArtifactType.SKILL in types
        assert ArtifactType.COMMAND in types
        assert ArtifactType.RULE not in types
        assert ArtifactType.AGENT not in types

    def test_detect_present(self, tmp_path: Path):
        (tmp_path / ".opencode").mkdir()
        with patch("loadout.adapters._base.Path.home", return_value=tmp_path):
            result = self.adapter.detect()
        assert result is not None
        assert result.name == "opencode"

    def test_get_target_path_skill(self, tmp_path: Path):
        artifact = Artifact(
            name="my-skill",
            artifact_type=ArtifactType.SKILL,
            source_path=tmp_path,
        )
        path = self.adapter.get_target_path(artifact, tmp_path / ".opencode")
        assert path == tmp_path / ".opencode" / "skills" / "my-skill"

    def test_get_target_path_command(self, tmp_path: Path):
        artifact = Artifact(
            name="my-cmd",
            artifact_type=ArtifactType.COMMAND,
            source_path=tmp_path / "cmd.md",
        )
        path = self.adapter.get_target_path(artifact, tmp_path / ".opencode")
        assert path == tmp_path / ".opencode" / "commands" / "my-cmd.md"

    def test_skips_rule(self, tmp_home: Path, sample_artifacts_dir: Path):
        agent = DetectedAgent(
            name="opencode",
            config_dir=tmp_home / ".opencode",
            display_name="OpenCode",
        )
        artifact = Artifact(
            name="auth-rule",
            artifact_type=ArtifactType.RULE,
            source_path=sample_artifacts_dir / "security" / "auth-rule" / "RULE.md",
            category="security",
        )
        result = self.adapter.install(artifact, agent)
        assert result.status == InstallStatus.SKIPPED

    def test_install_command(self, tmp_home: Path, sample_artifacts_dir: Path):
        agent = DetectedAgent(
            name="opencode",
            config_dir=tmp_home / ".opencode",
            display_name="OpenCode",
        )
        artifact = Artifact(
            name="my-command",
            artifact_type=ArtifactType.COMMAND,
            source_path=sample_artifacts_dir / "my-command" / "COMMAND.md",
            frontmatter=ArtifactFrontmatter(description="A test command"),
        )
        result = self.adapter.install(artifact, agent)
        assert result.status == InstallStatus.INSTALLED
        assert result.target_path is not None
        assert result.target_path.exists()
