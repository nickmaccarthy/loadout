"""Tests for the Cursor adapter."""

from pathlib import Path
from unittest.mock import patch

from loadout.adapters.cursor import CursorAdapter
from loadout.models import (
    Artifact,
    ArtifactFrontmatter,
    ArtifactType,
    DetectedAgent,
    InstallStatus,
)


class TestCursorAdapter:
    def setup_method(self):
        self.adapter = CursorAdapter()

    def test_properties(self):
        assert self.adapter.agent_name == "cursor"
        assert self.adapter.display_name == "Cursor"
        assert self.adapter.config_dir_name == ".cursor"

    def test_supported_types(self):
        types = self.adapter.supported_artifact_types()
        assert ArtifactType.SKILL in types
        assert ArtifactType.RULE in types
        assert ArtifactType.AGENT not in types
        assert ArtifactType.COMMAND not in types

    def test_detect_present(self, tmp_path: Path):
        (tmp_path / ".cursor").mkdir()
        with patch("loadout.adapters._base.Path.home", return_value=tmp_path):
            result = self.adapter.detect()
        assert result is not None
        assert result.name == "cursor"

    def test_get_target_path_rule_is_mdc(self, tmp_path: Path):
        artifact = Artifact(
            name="auth-rule",
            artifact_type=ArtifactType.RULE,
            source_path=tmp_path / "rule.md",
            category="security",
        )
        path = self.adapter.get_target_path(artifact, tmp_path / ".cursor")
        assert path == tmp_path / ".cursor" / "rules" / "security" / "auth-rule.mdc"

    def test_transform_content_rule(self, tmp_path: Path):
        artifact = Artifact(
            name="test-rule",
            artifact_type=ArtifactType.RULE,
            source_path=tmp_path / "rule.md",
            frontmatter=ArtifactFrontmatter(description="Test rule"),
        )
        content = "---\ndescription: Test rule\n---\n# Rule Content\n"
        result = self.adapter.transform_content(artifact, content)
        assert "description: Test rule" in result
        assert "alwaysApply: false" in result
        assert "# Rule Content" in result

    def test_transform_content_skill_unchanged(self, tmp_path: Path):
        artifact = Artifact(
            name="test-skill",
            artifact_type=ArtifactType.SKILL,
            source_path=tmp_path,
        )
        content = "# Skill Content\n"
        assert self.adapter.transform_content(artifact, content) == content

    def test_transform_filename_md_to_mdc(self, tmp_path: Path):
        artifact = Artifact(
            name="test",
            artifact_type=ArtifactType.RULE,
            source_path=tmp_path / "test.md",
        )
        assert self.adapter.transform_filename(artifact, "test.md") == "test.mdc"

    def test_transform_filename_skill_unchanged(self, tmp_path: Path):
        artifact = Artifact(
            name="test",
            artifact_type=ArtifactType.SKILL,
            source_path=tmp_path,
        )
        assert self.adapter.transform_filename(artifact, "helper.py") == "helper.py"

    def test_install_rule_creates_mdc(self, tmp_home: Path, sample_artifacts_dir: Path):
        agent = DetectedAgent(
            name="cursor",
            config_dir=tmp_home / ".cursor",
            display_name="Cursor",
        )
        artifact = Artifact(
            name="auth-rule",
            artifact_type=ArtifactType.RULE,
            source_path=sample_artifacts_dir / "security" / "auth-rule" / "RULE.md",
            category="security",
            frontmatter=ArtifactFrontmatter(description="Auth rule", always_apply=True),
        )
        result = self.adapter.install(artifact, agent)
        assert result.status == InstallStatus.INSTALLED
        assert result.target_path is not None
        assert result.target_path.suffix == ".mdc"

        content = result.target_path.read_text()
        assert "alwaysApply: true" in content

    def test_skips_unsupported_agent_type(self, tmp_home: Path, sample_artifacts_dir: Path):
        agent = DetectedAgent(
            name="cursor",
            config_dir=tmp_home / ".cursor",
            display_name="Cursor",
        )
        artifact = Artifact(
            name="my-agent",
            artifact_type=ArtifactType.AGENT,
            source_path=sample_artifacts_dir / "my-agent" / "AGENT.md",
        )
        result = self.adapter.install(artifact, agent)
        assert result.status == InstallStatus.SKIPPED
