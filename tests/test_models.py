"""Tests for data models."""

from pathlib import Path

from loadout.models import (
    Artifact,
    ArtifactFrontmatter,
    ArtifactType,
    DetectedAgent,
    InstallResult,
    InstallStatus,
    InstallSummary,
    Manifest,
    ManifestArtifact,
)


class TestArtifactType:
    def test_values(self):
        assert ArtifactType.SKILL == "skill"
        assert ArtifactType.RULE == "rule"
        assert ArtifactType.AGENT == "agent"
        assert ArtifactType.COMMAND == "command"


class TestInstallStatus:
    def test_values(self):
        assert InstallStatus.INSTALLED == "installed"
        assert InstallStatus.SKIPPED == "skipped"
        assert InstallStatus.FAILED == "failed"
        assert InstallStatus.ALREADY_EXISTS == "already_exists"


class TestArtifactFrontmatter:
    def test_defaults(self):
        fm = ArtifactFrontmatter()
        assert fm.description == ""
        assert fm.always_apply is False
        assert fm.globs == []
        assert fm.extra == {}

    def test_with_values(self):
        fm = ArtifactFrontmatter(
            description="test",
            always_apply=True,
            globs=["*.py"],
            extra={"custom": "value"},
        )
        assert fm.description == "test"
        assert fm.always_apply is True
        assert fm.globs == ["*.py"]
        assert fm.extra == {"custom": "value"}


class TestArtifact:
    def test_creation(self, tmp_path: Path):
        a = Artifact(
            name="test",
            artifact_type=ArtifactType.SKILL,
            source_path=tmp_path,
        )
        assert a.name == "test"
        assert a.artifact_type == ArtifactType.SKILL
        assert a.category == ""

    def test_frozen(self, tmp_path: Path):
        a = Artifact(
            name="test",
            artifact_type=ArtifactType.SKILL,
            source_path=tmp_path,
        )
        # Pydantic frozen model should prevent mutation
        try:
            a.name = "changed"  # type: ignore[misc]
            assert False, "Should have raised"
        except Exception:
            pass


class TestDetectedAgent:
    def test_creation(self, tmp_path: Path):
        agent = DetectedAgent(
            name="claude",
            config_dir=tmp_path / ".claude",
            display_name="Claude Code",
        )
        assert agent.name == "claude"
        assert agent.display_name == "Claude Code"


class TestInstallResult:
    def test_creation(self, tmp_path: Path):
        artifact = Artifact(
            name="test",
            artifact_type=ArtifactType.SKILL,
            source_path=tmp_path,
        )
        agent = DetectedAgent(name="claude", config_dir=tmp_path / ".claude")
        result = InstallResult(
            artifact=artifact,
            agent=agent,
            status=InstallStatus.INSTALLED,
            target_path=tmp_path / ".claude" / "skills" / "test",
        )
        assert result.status == InstallStatus.INSTALLED
        assert result.error is None


class TestInstallSummary:
    def test_properties(self, tmp_path: Path):
        artifact = Artifact(
            name="test",
            artifact_type=ArtifactType.SKILL,
            source_path=tmp_path,
        )
        agent = DetectedAgent(name="claude", config_dir=tmp_path / ".claude")

        summary = InstallSummary(
            results=[
                InstallResult(artifact=artifact, agent=agent, status=InstallStatus.INSTALLED),
                InstallResult(artifact=artifact, agent=agent, status=InstallStatus.SKIPPED),
                InstallResult(artifact=artifact, agent=agent, status=InstallStatus.FAILED),
                InstallResult(
                    artifact=artifact,
                    agent=agent,
                    status=InstallStatus.ALREADY_EXISTS,
                ),
            ]
        )
        assert len(summary.installed) == 1
        assert len(summary.skipped) == 1
        assert len(summary.failed) == 1
        assert len(summary.already_existed) == 1

    def test_empty(self):
        summary = InstallSummary()
        assert len(summary.installed) == 0
        assert len(summary.skipped) == 0
        assert len(summary.failed) == 0


class TestManifest:
    def test_creation(self):
        manifest = Manifest(
            artifacts=[
                ManifestArtifact(
                    name="test-skill",
                    type=ArtifactType.SKILL,
                    path="test-skill",
                )
            ]
        )
        assert len(manifest.artifacts) == 1
        assert manifest.artifacts[0].name == "test-skill"
