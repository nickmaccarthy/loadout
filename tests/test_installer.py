"""Tests for the installer module."""

from pathlib import Path
from unittest.mock import patch

from loadout.callbacks import NoOpCallbacks
from loadout.installer import install, install_all
from loadout.models import (
    Artifact,
    DetectedAgent,
)
from loadout.registry import get_default_registry


class TestInstall:
    def test_install_skill_to_claude(
        self, sample_skill_artifact: Artifact, claude_agent: DetectedAgent
    ):
        summary = install([sample_skill_artifact], [claude_agent])
        assert len(summary.installed) == 1
        result = summary.installed[0]
        assert result.target_path is not None
        assert result.target_path.exists()

    def test_install_rule_to_claude(
        self, sample_rule_artifact: Artifact, claude_agent: DetectedAgent
    ):
        summary = install([sample_rule_artifact], [claude_agent])
        assert len(summary.installed) == 1
        target = summary.installed[0].target_path
        assert target is not None
        assert target.name == "auth-rule.md"
        assert "security" in str(target)

    def test_install_skips_unsupported_type(
        self, sample_agent_artifact: Artifact, cursor_agent: DetectedAgent
    ):
        # Cursor doesn't support agent artifacts
        summary = install([sample_agent_artifact], [cursor_agent])
        assert len(summary.skipped) == 1

    def test_install_already_exists(
        self, sample_rule_artifact: Artifact, claude_agent: DetectedAgent
    ):
        # Install once
        install([sample_rule_artifact], [claude_agent])
        # Install again without force
        summary = install([sample_rule_artifact], [claude_agent])
        assert len(summary.already_existed) == 1

    def test_install_force_overwrites(
        self, sample_rule_artifact: Artifact, claude_agent: DetectedAgent
    ):
        install([sample_rule_artifact], [claude_agent])
        summary = install([sample_rule_artifact], [claude_agent], force=True)
        assert len(summary.installed) == 1

    def test_install_with_callbacks(
        self, sample_skill_artifact: Artifact, claude_agent: DetectedAgent
    ):
        callbacks = NoOpCallbacks()
        summary = install([sample_skill_artifact], [claude_agent], callbacks=callbacks)
        assert len(summary.installed) == 1

    def test_install_to_multiple_agents(
        self,
        sample_skill_artifact: Artifact,
        claude_agent: DetectedAgent,
        cursor_agent: DetectedAgent,
    ):
        summary = install([sample_skill_artifact], [claude_agent, cursor_agent])
        assert len(summary.installed) == 2

    def test_install_unknown_agent(self, sample_skill_artifact: Artifact, tmp_home: Path):
        unknown = DetectedAgent(
            name="unknown",
            config_dir=tmp_home / ".unknown",
        )
        summary = install([sample_skill_artifact], [unknown])
        assert len(summary.skipped) == 1


class TestInstallAll:
    def test_install_all(self, sample_artifacts_dir: Path, tmp_home: Path):
        registry = get_default_registry()
        with patch("loadout.adapters._base.Path.home", return_value=tmp_home):
            summary = install_all(sample_artifacts_dir, registry=registry)

        # 4 artifacts * 3 agents, but some combos are unsupported/skipped
        assert len(summary.results) > 0
        assert len(summary.installed) > 0
