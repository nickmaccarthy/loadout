"""Agent adapter abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from loadout.models import Artifact, ArtifactType, CheckResult, DetectedAgent, InstallResult


class AgentAdapter(ABC):
    """Abstract base class for coding agent adapters.

    Each supported agent (Claude Code, Cursor, OpenCode, etc.) implements
    this interface. The adapter handles detection, path resolution,
    content transformation, and installation for its agent.
    """

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Unique identifier for this agent (e.g. 'claude', 'cursor')."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name (e.g. 'Claude Code', 'Cursor')."""

    @property
    @abstractmethod
    def config_dir_name(self) -> str:
        """Name of the config directory (e.g. '.claude', '.cursor')."""

    @abstractmethod
    def supported_artifact_types(self) -> set[ArtifactType]:
        """Return the set of artifact types this agent supports."""

    @abstractmethod
    def detect(self) -> DetectedAgent | None:
        """Detect if this agent is installed on the system.

        Returns a DetectedAgent if found, None otherwise.
        """

    @abstractmethod
    def get_target_path(self, artifact: Artifact, config_dir: Path) -> Path:
        """Resolve the target installation path for an artifact."""

    @abstractmethod
    def transform_content(self, artifact: Artifact, content: str) -> str:
        """Transform artifact content for this agent's format."""

    @abstractmethod
    def transform_filename(self, artifact: Artifact, filename: str) -> str:
        """Transform artifact filename for this agent's format."""

    @abstractmethod
    def install(
        self, artifact: Artifact, agent: DetectedAgent, force: bool = False
    ) -> InstallResult:
        """Install an artifact to this agent."""

    @abstractmethod
    def check(self, artifact: Artifact, agent: DetectedAgent) -> CheckResult:
        """Check if an installed artifact is current, stale, or missing."""
