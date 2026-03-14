"""Artifact scanning and agent detection."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from loadout._transforms import parse_frontmatter
from loadout.exceptions import ArtifactNotFoundError, ManifestError
from loadout.models import (
    Artifact,
    ArtifactType,
    DetectedAgent,
    Manifest,
    ManifestArtifact,
)
from loadout.registry import AdapterRegistry, get_default_registry

# Marker files that indicate artifact type and serve as the artifact content
_MARKER_FILES: dict[str, ArtifactType] = {
    "SKILL.md": ArtifactType.SKILL,
    "RULE.md": ArtifactType.RULE,
    "AGENT.md": ArtifactType.AGENT,
    "COMMAND.md": ArtifactType.COMMAND,
}


def discover_artifacts(source_dir: str | Path) -> list[Artifact]:
    """Scan a directory for artifacts.

    Discovers artifacts by looking for:
    1. A loadout.yaml manifest (if present, used exclusively)
    2. Marker files (SKILL.md, RULE.md, AGENT.md, COMMAND.md)

    Args:
        source_dir: Directory to scan for artifacts.

    Returns:
        List of discovered Artifact objects.
    """
    source_dir = Path(source_dir)
    if not source_dir.is_dir():
        raise ArtifactNotFoundError(str(source_dir))

    manifest_path = source_dir / "loadout.yaml"
    if manifest_path.is_file():
        return _discover_from_manifest(manifest_path, source_dir)

    return _discover_from_markers(source_dir)


def _discover_from_manifest(manifest_path: Path, source_dir: Path) -> list[Artifact]:
    """Discover artifacts from a loadout.yaml manifest."""
    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise ManifestError(f"Invalid manifest YAML: {e}") from e

    if not isinstance(raw, dict) or "artifacts" not in raw:
        raise ManifestError("Manifest must contain an 'artifacts' key")

    try:
        manifest = Manifest(artifacts=[ManifestArtifact(**entry) for entry in raw["artifacts"]])
    except (TypeError, ValidationError) as e:
        raise ManifestError(f"Invalid manifest structure: {e}") from e

    artifacts = []
    for entry in manifest.artifacts:
        artifact_path = source_dir / entry.path
        if not artifact_path.exists():
            raise ArtifactNotFoundError(str(artifact_path))

        fm_content = ""
        if artifact_path.is_file():
            fm_content = artifact_path.read_text(encoding="utf-8")
        elif artifact_path.is_dir():
            # Look for a marker file inside for frontmatter
            for marker_name in _MARKER_FILES:
                marker = artifact_path / marker_name
                if marker.is_file():
                    fm_content = marker.read_text(encoding="utf-8")
                    break

        frontmatter, _ = parse_frontmatter(fm_content) if fm_content else (None, "")

        from loadout.models import ArtifactFrontmatter

        if entry.description and frontmatter:
            frontmatter.description = entry.description
        elif entry.description:
            frontmatter = ArtifactFrontmatter(description=entry.description)

        artifacts.append(
            Artifact(
                name=entry.name,
                artifact_type=entry.type,
                source_path=artifact_path,
                category=entry.category,
                frontmatter=frontmatter or ArtifactFrontmatter(),
            )
        )

    return artifacts


def _discover_from_markers(source_dir: Path) -> list[Artifact]:
    """Discover artifacts by scanning for marker files."""
    artifacts = []

    for marker_name, artifact_type in _MARKER_FILES.items():
        for marker_path in source_dir.rglob(marker_name):
            parent = marker_path.parent
            name = parent.name

            content = marker_path.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(content)

            # Derive category from directory structure
            # e.g., source_dir/rules/security/my-rule/RULE.md -> category = "security"
            rel = parent.relative_to(source_dir)
            parts = rel.parts
            category = parts[-2] if len(parts) >= 2 else ""

            if artifact_type == ArtifactType.SKILL:
                # Skills are directories
                source_path = parent
            else:
                # Rules/agents/commands are files (the marker itself)
                source_path = marker_path

            artifacts.append(
                Artifact(
                    name=name,
                    artifact_type=artifact_type,
                    source_path=source_path,
                    category=category,
                    frontmatter=frontmatter,
                )
            )

    return sorted(artifacts, key=lambda a: (a.artifact_type.value, a.name))


def detect_agents(registry: AdapterRegistry | None = None) -> list[DetectedAgent]:
    """Detect which coding agents are installed on the system.

    Args:
        registry: Adapter registry to use. Defaults to the built-in registry.

    Returns:
        List of detected agents.
    """
    if registry is None:
        registry = get_default_registry()

    agents = []
    for adapter in registry.all():
        detected = adapter.detect()
        if detected is not None:
            agents.append(detected)

    return agents
