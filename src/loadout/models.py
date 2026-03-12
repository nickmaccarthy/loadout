"""Data models for loadout."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """Types of artifacts that can be installed."""

    SKILL = "skill"
    RULE = "rule"
    AGENT = "agent"
    COMMAND = "command"


class InstallStatus(str, Enum):
    """Result status of an artifact installation."""

    INSTALLED = "installed"
    SKIPPED = "skipped"
    FAILED = "failed"
    ALREADY_EXISTS = "already_exists"


class ArtifactFrontmatter(BaseModel):
    """Parsed frontmatter from an artifact file."""

    description: str = ""
    always_apply: bool = False
    globs: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)


class Artifact(BaseModel):
    """An artifact discovered from a source directory."""

    name: str
    artifact_type: ArtifactType
    source_path: Path
    category: str = ""
    frontmatter: ArtifactFrontmatter = Field(default_factory=ArtifactFrontmatter)

    model_config = {"frozen": True}


class DetectedAgent(BaseModel):
    """A coding agent detected on the system."""

    name: str
    config_dir: Path
    display_name: str = ""


class InstallResult(BaseModel):
    """Result of installing a single artifact to a single agent."""

    artifact: Artifact
    agent: DetectedAgent
    status: InstallStatus
    target_path: Path | None = None
    error: str | None = None


class InstallSummary(BaseModel):
    """Summary of a batch install operation."""

    results: list[InstallResult] = Field(default_factory=list)

    @property
    def installed(self) -> list[InstallResult]:
        return [r for r in self.results if r.status == InstallStatus.INSTALLED]

    @property
    def skipped(self) -> list[InstallResult]:
        return [r for r in self.results if r.status == InstallStatus.SKIPPED]

    @property
    def failed(self) -> list[InstallResult]:
        return [r for r in self.results if r.status == InstallStatus.FAILED]

    @property
    def already_existed(self) -> list[InstallResult]:
        return [r for r in self.results if r.status == InstallStatus.ALREADY_EXISTS]


class ManifestArtifact(BaseModel):
    """An artifact entry in a loadout.yaml manifest."""

    name: str
    type: ArtifactType
    path: str
    category: str = ""
    description: str = ""


class Manifest(BaseModel):
    """A loadout.yaml manifest defining artifacts explicitly."""

    artifacts: list[ManifestArtifact] = Field(default_factory=list)
