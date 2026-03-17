"""Core check functions for comparing source and installed artifacts."""

from __future__ import annotations

from pathlib import Path

from loadout.callbacks import LoadoutCallbacks, NoOpCallbacks
from loadout.discovery import detect_agents, discover_artifacts
from loadout.models import (
    Artifact,
    CheckResult,
    CheckStatus,
    CheckSummary,
    DetectedAgent,
)
from loadout.registry import AdapterRegistry, get_default_registry


def check(
    artifacts: list[Artifact],
    agents: list[DetectedAgent],
    *,
    registry: AdapterRegistry | None = None,
    callbacks: LoadoutCallbacks | None = None,
) -> CheckSummary:
    """Check artifacts against installed versions for each agent.

    Compares source artifact content (after transforms) against what
    is currently installed. Reports each artifact/agent pair as
    current, stale, missing, or unknown.

    Args:
        artifacts: Artifacts to check.
        agents: Target agents to check against.
        registry: Adapter registry. Defaults to built-in.
        callbacks: Optional lifecycle callbacks.

    Returns:
        CheckSummary with results for each artifact/agent combination.
    """
    if registry is None:
        registry = get_default_registry()
    cb = callbacks or NoOpCallbacks()

    summary = CheckSummary()

    for artifact in artifacts:
        for agent in agents:
            if not registry.has(agent.name):
                summary.results.append(
                    CheckResult(
                        artifact=artifact,
                        agent=agent,
                        status=CheckStatus.UNKNOWN,
                    )
                )
                continue

            adapter = registry.get(agent.name)

            try:
                result = adapter.check(artifact, agent)
            except Exception:
                result = CheckResult(
                    artifact=artifact,
                    agent=agent,
                    status=CheckStatus.UNKNOWN,
                )

            summary.results.append(result)
            cb.on_check_complete(result)

    return summary


def check_all(
    source_dir: str | Path,
    *,
    registry: AdapterRegistry | None = None,
    callbacks: LoadoutCallbacks | None = None,
) -> CheckSummary:
    """Discover artifacts, detect all agents, check everything.

    Args:
        source_dir: Directory containing artifacts.
        registry: Adapter registry. Defaults to built-in.
        callbacks: Optional lifecycle callbacks.

    Returns:
        CheckSummary with all results.
    """
    if registry is None:
        registry = get_default_registry()

    artifacts = discover_artifacts(source_dir)
    agents = detect_agents(registry)

    return check(
        artifacts=artifacts,
        agents=agents,
        registry=registry,
        callbacks=callbacks,
    )
