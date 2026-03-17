"""Tests for the checker module."""

from pathlib import Path
from unittest.mock import patch

from loadout.callbacks import NoOpCallbacks
from loadout.checker import check, check_all
from loadout.installer import install
from loadout.models import (
    Artifact,
    CheckStatus,
    DetectedAgent,
)
from loadout.registry import get_default_registry


class TestCheck:
    def test_check_missing_artifact(
        self, sample_skill_artifact: Artifact, claude_agent: DetectedAgent
    ):
        summary = check([sample_skill_artifact], [claude_agent])
        assert len(summary.missing) == 1
        assert summary.missing[0].status == CheckStatus.MISSING

    def test_check_current_after_install(
        self, sample_skill_artifact: Artifact, claude_agent: DetectedAgent
    ):
        install([sample_skill_artifact], [claude_agent])
        summary = check([sample_skill_artifact], [claude_agent])
        assert len(summary.current) == 1
        assert summary.current[0].source_hash is not None
        assert summary.current[0].installed_hash is not None
        assert summary.current[0].source_hash == summary.current[0].installed_hash

    def test_check_stale_after_modification(
        self, sample_skill_artifact: Artifact, claude_agent: DetectedAgent
    ):
        install([sample_skill_artifact], [claude_agent])

        # Modify the installed file to make it stale
        target_dir = claude_agent.config_dir / "skills" / "my-skill"
        skill_file = target_dir / "SKILL.md"
        skill_file.write_text("modified content\n")

        summary = check([sample_skill_artifact], [claude_agent])
        assert len(summary.stale) == 1
        assert summary.stale[0].source_hash != summary.stale[0].installed_hash

    def test_check_rule_missing(self, sample_rule_artifact: Artifact, claude_agent: DetectedAgent):
        summary = check([sample_rule_artifact], [claude_agent])
        assert len(summary.missing) == 1

    def test_check_rule_current_after_install(
        self, sample_rule_artifact: Artifact, claude_agent: DetectedAgent
    ):
        install([sample_rule_artifact], [claude_agent])
        summary = check([sample_rule_artifact], [claude_agent])
        assert len(summary.current) == 1

    def test_check_rule_stale_after_modification(
        self, sample_rule_artifact: Artifact, claude_agent: DetectedAgent
    ):
        install([sample_rule_artifact], [claude_agent])

        target = claude_agent.config_dir / "rules" / "security" / "auth-rule.md"
        target.write_text("modified content\n")

        summary = check([sample_rule_artifact], [claude_agent])
        assert len(summary.stale) == 1

    def test_check_unsupported_type_returns_unknown(
        self, sample_agent_artifact: Artifact, cursor_agent: DetectedAgent
    ):
        summary = check([sample_agent_artifact], [cursor_agent])
        assert len(summary.unknown) == 1

    def test_check_unknown_agent(self, sample_skill_artifact: Artifact, tmp_home: Path):
        unknown = DetectedAgent(
            name="unknown",
            config_dir=tmp_home / ".unknown",
        )
        summary = check([sample_skill_artifact], [unknown])
        assert len(summary.unknown) == 1

    def test_check_multiple_agents(
        self,
        sample_skill_artifact: Artifact,
        claude_agent: DetectedAgent,
        cursor_agent: DetectedAgent,
    ):
        install([sample_skill_artifact], [claude_agent, cursor_agent])
        summary = check([sample_skill_artifact], [claude_agent, cursor_agent])
        assert len(summary.current) == 2

    def test_check_with_callbacks(
        self, sample_skill_artifact: Artifact, claude_agent: DetectedAgent
    ):
        callbacks = NoOpCallbacks()
        summary = check([sample_skill_artifact], [claude_agent], callbacks=callbacks)
        assert len(summary.results) == 1

    def test_check_mixed_results(
        self,
        sample_skill_artifact: Artifact,
        sample_rule_artifact: Artifact,
        claude_agent: DetectedAgent,
    ):
        # Install only the skill
        install([sample_skill_artifact], [claude_agent])

        summary = check([sample_skill_artifact, sample_rule_artifact], [claude_agent])
        assert len(summary.current) == 1
        assert len(summary.missing) == 1
        assert summary.current[0].artifact.name == "my-skill"
        assert summary.missing[0].artifact.name == "auth-rule"


class TestCheckAll:
    def test_check_all_nothing_installed(self, sample_artifacts_dir: Path, tmp_home: Path):
        registry = get_default_registry()
        with patch("loadout.adapters._base.Path.home", return_value=tmp_home):
            summary = check_all(sample_artifacts_dir, registry=registry)

        assert len(summary.results) > 0
        # Nothing installed, so everything should be missing or unknown
        for result in summary.results:
            assert result.status in (CheckStatus.MISSING, CheckStatus.UNKNOWN)

    def test_check_all_after_install(self, sample_artifacts_dir: Path, tmp_home: Path):
        from loadout.installer import install_all

        registry = get_default_registry()
        with patch("loadout.adapters._base.Path.home", return_value=tmp_home):
            install_all(sample_artifacts_dir, registry=registry)
            summary = check_all(sample_artifacts_dir, registry=registry)

        assert len(summary.current) > 0
