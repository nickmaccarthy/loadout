"""loadout - Install artifacts into coding agents."""

from loadout._version import __version__
from loadout.adapters import AgentAdapter, ClaudeCodeAdapter, CursorAdapter, OpenCodeAdapter
from loadout.callbacks import LoadoutCallbacks, NoOpCallbacks
from loadout.checker import check, check_all
from loadout.discovery import detect_agents, discover_artifacts
from loadout.exceptions import (
    AdapterAlreadyRegisteredError,
    AdapterNotFoundError,
    ArtifactNotFoundError,
    InstallError,
    LoadoutError,
    ManifestError,
    TransformError,
)
from loadout.installer import install, install_all, install_interactive
from loadout.models import (
    Artifact,
    ArtifactFrontmatter,
    ArtifactType,
    CheckResult,
    CheckStatus,
    CheckSummary,
    DetectedAgent,
    InstallResult,
    InstallStatus,
    InstallSummary,
    Manifest,
)
from loadout.registry import AdapterRegistry, get_default_registry

__all__ = [
    "__version__",
    # Adapters
    "AgentAdapter",
    "ClaudeCodeAdapter",
    "CursorAdapter",
    "OpenCodeAdapter",
    # Callbacks
    "LoadoutCallbacks",
    "NoOpCallbacks",
    # Checker
    "check",
    "check_all",
    # Discovery
    "detect_agents",
    "discover_artifacts",
    # Exceptions
    "AdapterAlreadyRegisteredError",
    "AdapterNotFoundError",
    "ArtifactNotFoundError",
    "InstallError",
    "LoadoutError",
    "ManifestError",
    "TransformError",
    # Installer
    "install",
    "install_all",
    "install_interactive",
    # Models
    "Artifact",
    "ArtifactFrontmatter",
    "ArtifactType",
    "CheckResult",
    "CheckStatus",
    "CheckSummary",
    "DetectedAgent",
    "InstallResult",
    "InstallStatus",
    "InstallSummary",
    "Manifest",
    # Registry
    "AdapterRegistry",
    "get_default_registry",
]
