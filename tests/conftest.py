"""Shared test fixtures for loadout tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loadout.models import (
    Artifact,
    ArtifactFrontmatter,
    ArtifactType,
    DetectedAgent,
)


@pytest.fixture
def tmp_home(tmp_path: Path) -> Path:
    """Create a temporary home directory with mock agent configs."""
    # Claude Code
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "skills").mkdir()
    (claude_dir / "rules").mkdir()
    (claude_dir / "agents").mkdir()
    (claude_dir / "commands").mkdir()

    # Cursor
    cursor_dir = tmp_path / ".cursor"
    cursor_dir.mkdir()
    (cursor_dir / "skills").mkdir()
    (cursor_dir / "rules").mkdir()

    # OpenCode
    opencode_dir = tmp_path / ".opencode"
    opencode_dir.mkdir()
    (opencode_dir / "skills").mkdir()
    (opencode_dir / "commands").mkdir()

    return tmp_path


@pytest.fixture
def sample_artifacts_dir(tmp_path: Path) -> Path:
    """Create a directory with sample artifacts for discovery."""
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()

    # Skill (directory with marker)
    skill_dir = artifacts_dir / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\ndescription: A test skill\n---\n# My Skill\nDoes things.\n"
    )
    (skill_dir / "helper.py").write_text("def helper(): pass\n")

    # Rule (directory with marker)
    rules_dir = artifacts_dir / "security"
    rules_dir.mkdir()
    rule_dir = rules_dir / "auth-rule"
    rule_dir.mkdir()
    (rule_dir / "RULE.md").write_text(
        "---\ndescription: Auth rule\nalways_apply: true\n---\n# Auth Rule\nCheck auth.\n"
    )

    # Agent (directory with marker)
    agent_dir = artifacts_dir / "my-agent"
    agent_dir.mkdir()
    (agent_dir / "AGENT.md").write_text(
        "---\ndescription: A test agent\n---\n# My Agent\nDoes agent things.\n"
    )

    # Command (directory with marker)
    cmd_dir = artifacts_dir / "my-command"
    cmd_dir.mkdir()
    (cmd_dir / "COMMAND.md").write_text(
        "---\ndescription: A test command\n---\n# My Command\nRuns a command.\n"
    )

    return artifacts_dir


@pytest.fixture
def sample_skill_artifact(sample_artifacts_dir: Path) -> Artifact:
    """A sample skill artifact."""
    return Artifact(
        name="my-skill",
        artifact_type=ArtifactType.SKILL,
        source_path=sample_artifacts_dir / "my-skill",
        frontmatter=ArtifactFrontmatter(description="A test skill"),
    )


@pytest.fixture
def sample_rule_artifact(sample_artifacts_dir: Path) -> Artifact:
    """A sample rule artifact."""
    return Artifact(
        name="auth-rule",
        artifact_type=ArtifactType.RULE,
        source_path=sample_artifacts_dir / "security" / "auth-rule" / "RULE.md",
        category="security",
        frontmatter=ArtifactFrontmatter(description="Auth rule", always_apply=True),
    )


@pytest.fixture
def sample_agent_artifact(sample_artifacts_dir: Path) -> Artifact:
    """A sample agent artifact."""
    return Artifact(
        name="my-agent",
        artifact_type=ArtifactType.AGENT,
        source_path=sample_artifacts_dir / "my-agent" / "AGENT.md",
        frontmatter=ArtifactFrontmatter(description="A test agent"),
    )


@pytest.fixture
def sample_command_artifact(sample_artifacts_dir: Path) -> Artifact:
    """A sample command artifact."""
    return Artifact(
        name="my-command",
        artifact_type=ArtifactType.COMMAND,
        source_path=sample_artifacts_dir / "my-command" / "COMMAND.md",
        frontmatter=ArtifactFrontmatter(description="A test command"),
    )


@pytest.fixture
def claude_agent(tmp_home: Path) -> DetectedAgent:
    """A detected Claude Code agent."""
    return DetectedAgent(
        name="claude",
        config_dir=tmp_home / ".claude",
        display_name="Claude Code",
    )


@pytest.fixture
def cursor_agent(tmp_home: Path) -> DetectedAgent:
    """A detected Cursor agent."""
    return DetectedAgent(
        name="cursor",
        config_dir=tmp_home / ".cursor",
        display_name="Cursor",
    )


@pytest.fixture
def opencode_agent(tmp_home: Path) -> DetectedAgent:
    """A detected OpenCode agent."""
    return DetectedAgent(
        name="opencode",
        config_dir=tmp_home / ".opencode",
        display_name="OpenCode",
    )
