"""Tests for the Claude Code adapter."""

from pathlib import Path
from unittest.mock import patch

from loadout.adapters.claude import ClaudeCodeAdapter
from loadout.models import (
    Artifact,
    ArtifactFrontmatter,
    ArtifactType,
    DetectedAgent,
    InstallStatus,
)


class TestClaudeCodeAdapter:
    def setup_method(self):
        self.adapter = ClaudeCodeAdapter()

    def test_properties(self):
        assert self.adapter.agent_name == "claude"
        assert self.adapter.display_name == "Claude Code"
        assert self.adapter.config_dir_name == ".claude"

    def test_supported_types(self):
        types = self.adapter.supported_artifact_types()
        assert ArtifactType.SKILL in types
        assert ArtifactType.RULE in types
        assert ArtifactType.AGENT in types
        assert ArtifactType.COMMAND in types

    def test_detect_present(self, tmp_path: Path):
        (tmp_path / ".claude").mkdir()
        with patch("loadout.adapters._base.Path.home", return_value=tmp_path):
            result = self.adapter.detect()
        assert result is not None
        assert result.name == "claude"

    def test_detect_absent(self, tmp_path: Path):
        with patch("loadout.adapters._base.Path.home", return_value=tmp_path):
            result = self.adapter.detect()
        assert result is None

    def test_get_target_path_skill(self, tmp_path: Path):
        artifact = Artifact(
            name="my-skill",
            artifact_type=ArtifactType.SKILL,
            source_path=tmp_path,
        )
        path = self.adapter.get_target_path(artifact, tmp_path / ".claude")
        assert path == tmp_path / ".claude" / "skills" / "my-skill"

    def test_get_target_path_rule_with_category(self, tmp_path: Path):
        artifact = Artifact(
            name="auth-rule",
            artifact_type=ArtifactType.RULE,
            source_path=tmp_path / "rule.md",
            category="security",
        )
        path = self.adapter.get_target_path(artifact, tmp_path / ".claude")
        assert path == tmp_path / ".claude" / "rules" / "security" / "auth-rule.md"

    def test_get_target_path_command(self, tmp_path: Path):
        artifact = Artifact(
            name="my-cmd",
            artifact_type=ArtifactType.COMMAND,
            source_path=tmp_path / "cmd.md",
        )
        path = self.adapter.get_target_path(artifact, tmp_path / ".claude")
        assert path == tmp_path / ".claude" / "commands" / "my-cmd.md"

    def test_install_skill_directory(self, tmp_home: Path, sample_artifacts_dir: Path):
        agent = DetectedAgent(
            name="claude",
            config_dir=tmp_home / ".claude",
            display_name="Claude Code",
        )
        artifact = Artifact(
            name="my-skill",
            artifact_type=ArtifactType.SKILL,
            source_path=sample_artifacts_dir / "my-skill",
            frontmatter=ArtifactFrontmatter(description="A test skill"),
        )
        result = self.adapter.install(artifact, agent)
        assert result.status == InstallStatus.INSTALLED
        assert result.target_path is not None
        assert result.target_path.is_dir()
        assert (result.target_path / "SKILL.md").exists()
        assert (result.target_path / "helper.py").exists()

    def test_install_skill_directory_with_binary_file(self, tmp_home: Path, tmp_path: Path):
        skill_dir = tmp_path / "binary-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        expected_bytes = b"\xff\xfe\x00\x01"
        (skill_dir / "logo.bin").write_bytes(expected_bytes)

        agent = DetectedAgent(
            name="claude",
            config_dir=tmp_home / ".claude",
            display_name="Claude Code",
        )
        artifact = Artifact(
            name="binary-skill",
            artifact_type=ArtifactType.SKILL,
            source_path=skill_dir,
        )

        result = self.adapter.install(artifact, agent)

        assert result.status == InstallStatus.INSTALLED
        assert result.target_path is not None
        assert (result.target_path / "logo.bin").read_bytes() == expected_bytes

    def test_content_unchanged(self, tmp_path: Path):
        artifact = Artifact(
            name="test",
            artifact_type=ArtifactType.RULE,
            source_path=tmp_path / "test.md",
        )
        content = "# Original Content\nKeep this exact text."
        assert self.adapter.transform_content(artifact, content) == content

    def test_filename_unchanged(self, tmp_path: Path):
        artifact = Artifact(
            name="test",
            artifact_type=ArtifactType.RULE,
            source_path=tmp_path / "test.md",
        )
        assert self.adapter.transform_filename(artifact, "test.md") == "test.md"
