"""Tests for artifact discovery and agent detection."""

from pathlib import Path
from unittest.mock import patch

import pytest

from loadout.discovery import detect_agents, discover_artifacts
from loadout.exceptions import ArtifactNotFoundError, ManifestError
from loadout.models import ArtifactType
from loadout.registry import get_default_registry


class TestDiscoverArtifacts:
    def test_discover_from_markers(self, sample_artifacts_dir: Path):
        artifacts = discover_artifacts(sample_artifacts_dir)
        assert len(artifacts) == 4

        types = {a.artifact_type for a in artifacts}
        assert ArtifactType.SKILL in types
        assert ArtifactType.RULE in types
        assert ArtifactType.AGENT in types
        assert ArtifactType.COMMAND in types

    def test_skill_is_directory(self, sample_artifacts_dir: Path):
        artifacts = discover_artifacts(sample_artifacts_dir)
        skill = next(a for a in artifacts if a.artifact_type == ArtifactType.SKILL)
        assert skill.source_path.is_dir()
        assert skill.name == "my-skill"

    def test_rule_has_category(self, sample_artifacts_dir: Path):
        artifacts = discover_artifacts(sample_artifacts_dir)
        rule = next(a for a in artifacts if a.artifact_type == ArtifactType.RULE)
        assert rule.category == "security"

    def test_frontmatter_parsed(self, sample_artifacts_dir: Path):
        artifacts = discover_artifacts(sample_artifacts_dir)
        skill = next(a for a in artifacts if a.artifact_type == ArtifactType.SKILL)
        assert skill.frontmatter.description == "A test skill"

    def test_nonexistent_dir_raises(self, tmp_path: Path):
        with pytest.raises(ArtifactNotFoundError):
            discover_artifacts(tmp_path / "nonexistent")

    def test_empty_dir_returns_empty(self, tmp_path: Path):
        empty = tmp_path / "empty"
        empty.mkdir()
        assert discover_artifacts(empty) == []

    def test_discover_from_manifest(self, tmp_path: Path):
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        skill_dir = artifacts_dir / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\ndescription: Manifest skill\n---\n# Skill\n")

        manifest = artifacts_dir / "loadout.yaml"
        manifest.write_text(
            "artifacts:\n  - name: my-skill\n    type: skill\n    path: my-skill\n"
        )

        artifacts = discover_artifacts(artifacts_dir)
        assert len(artifacts) == 1
        assert artifacts[0].name == "my-skill"

    def test_invalid_manifest_raises(self, tmp_path: Path):
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()
        (artifacts_dir / "loadout.yaml").write_text("not: valid: yaml: [")
        with pytest.raises(ManifestError):
            discover_artifacts(artifacts_dir)

    def test_manifest_missing_artifacts_key(self, tmp_path: Path):
        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()
        (artifacts_dir / "loadout.yaml").write_text("name: test\n")
        with pytest.raises(ManifestError, match="artifacts"):
            discover_artifacts(artifacts_dir)


class TestDetectAgents:
    def test_detects_agents(self, tmp_home: Path):
        registry = get_default_registry()
        with patch("loadout.adapters._base.Path.home", return_value=tmp_home):
            agents = detect_agents(registry)

        names = {a.name for a in agents}
        assert "claude" in names
        assert "cursor" in names
        assert "opencode" in names

    def test_detects_only_existing(self, tmp_path: Path):
        # Only create claude config
        (tmp_path / ".claude").mkdir()

        registry = get_default_registry()
        with patch("loadout.adapters._base.Path.home", return_value=tmp_path):
            agents = detect_agents(registry)

        assert len(agents) == 1
        assert agents[0].name == "claude"

    def test_no_agents_detected(self, tmp_path: Path):
        registry = get_default_registry()
        with patch("loadout.adapters._base.Path.home", return_value=tmp_path):
            agents = detect_agents(registry)

        assert agents == []
