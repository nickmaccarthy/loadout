"""Core installation functions."""

from __future__ import annotations

from pathlib import Path

from loadout.callbacks import LoadoutCallbacks, NoOpCallbacks
from loadout.discovery import detect_agents, discover_artifacts
from loadout.models import (
    Artifact,
    DetectedAgent,
    InstallResult,
    InstallStatus,
    InstallSummary,
)
from loadout.registry import AdapterRegistry, get_default_registry


def install(
    artifacts: list[Artifact],
    agents: list[DetectedAgent],
    *,
    force: bool = False,
    registry: AdapterRegistry | None = None,
    callbacks: LoadoutCallbacks | None = None,
) -> InstallSummary:
    """Install artifacts to specified agents.

    This is the headless API - the caller handles all UX.

    Args:
        artifacts: Artifacts to install.
        agents: Target agents to install to.
        force: Overwrite existing artifacts.
        registry: Adapter registry. Defaults to built-in.
        callbacks: Optional lifecycle callbacks.

    Returns:
        InstallSummary with results for each artifact/agent combination.
    """
    if registry is None:
        registry = get_default_registry()
    cb = callbacks or NoOpCallbacks()

    summary = InstallSummary()

    for artifact in artifacts:
        cb.on_artifact_discovered(artifact)

        for agent in agents:
            cb.on_agent_detected(agent)

            if not registry.has(agent.name):
                summary.results.append(
                    InstallResult(
                        artifact=artifact,
                        agent=agent,
                        status=InstallStatus.SKIPPED,
                        error=f"No adapter for agent: {agent.name}",
                    )
                )
                continue

            adapter = registry.get(agent.name)
            cb.on_install_started(artifact, agent)

            try:
                result = adapter.install(artifact, agent, force=force)
            except Exception as e:
                result = InstallResult(
                    artifact=artifact,
                    agent=agent,
                    status=InstallStatus.FAILED,
                    error=str(e),
                )
            summary.results.append(result)

            if result.status == InstallStatus.INSTALLED:
                cb.on_install_complete(result)
            elif result.status in (InstallStatus.SKIPPED, InstallStatus.ALREADY_EXISTS):
                cb.on_install_skipped(result)
            elif result.status == InstallStatus.FAILED:
                cb.on_install_failed(result)

    return summary


def install_all(
    source_dir: str | Path,
    *,
    force: bool = False,
    registry: AdapterRegistry | None = None,
    callbacks: LoadoutCallbacks | None = None,
) -> InstallSummary:
    """Discover artifacts, detect all agents, install everything.

    Yolo mode - installs all discovered artifacts to all detected agents.

    Args:
        source_dir: Directory containing artifacts.
        force: Overwrite existing artifacts.
        registry: Adapter registry. Defaults to built-in.
        callbacks: Optional lifecycle callbacks.

    Returns:
        InstallSummary with all results.
    """
    if registry is None:
        registry = get_default_registry()

    artifacts = discover_artifacts(source_dir)
    agents = detect_agents(registry)

    return install(
        artifacts=artifacts,
        agents=agents,
        force=force,
        registry=registry,
        callbacks=callbacks,
    )


def install_interactive(
    source_dir: str | Path,
    *,
    force: bool = False,
    registry: AdapterRegistry | None = None,
    callbacks: LoadoutCallbacks | None = None,
) -> InstallSummary:
    """Interactive installation with agent selection prompt.

    Uses questionary to present a checkbox prompt for agent selection.
    Requires the `loadout[interactive]` extra.

    Args:
        source_dir: Directory containing artifacts.
        force: Overwrite existing artifacts.
        registry: Adapter registry. Defaults to built-in.
        callbacks: Optional lifecycle callbacks.

    Returns:
        InstallSummary with results.

    Raises:
        ImportError: If questionary is not installed.
    """
    from loadout._prompts import prompt_agent_selection

    if registry is None:
        registry = get_default_registry()

    artifacts = discover_artifacts(source_dir)
    agents = detect_agents(registry)

    if not agents:
        return InstallSummary()

    if not artifacts:
        return InstallSummary()

    selected = prompt_agent_selection(agents)
    if not selected:
        return InstallSummary()

    return install(
        artifacts=artifacts,
        agents=selected,
        force=force,
        registry=registry,
        callbacks=callbacks,
    )
