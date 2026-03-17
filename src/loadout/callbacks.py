"""Callback protocol for lifecycle events during installation."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from loadout.models import Artifact, CheckResult, DetectedAgent, InstallResult


@runtime_checkable
class LoadoutCallbacks(Protocol):
    """Protocol for receiving lifecycle events during installation.

    CLIs implement this to provide custom messaging/progress.
    All methods have default no-op behavior so implementers
    only need to override the hooks they care about.
    """

    def on_artifact_discovered(self, artifact: Artifact) -> None: ...

    def on_agent_detected(self, agent: DetectedAgent) -> None: ...

    def on_install_started(self, artifact: Artifact, agent: DetectedAgent) -> None: ...

    def on_install_complete(self, result: InstallResult) -> None: ...

    def on_install_skipped(self, result: InstallResult) -> None: ...

    def on_install_failed(self, result: InstallResult) -> None: ...

    def on_check_complete(self, result: CheckResult) -> None: ...


class NoOpCallbacks:
    """Default no-op implementation of LoadoutCallbacks."""

    def on_artifact_discovered(self, artifact: Artifact) -> None:
        pass

    def on_agent_detected(self, agent: DetectedAgent) -> None:
        pass

    def on_install_started(self, artifact: Artifact, agent: DetectedAgent) -> None:
        pass

    def on_install_complete(self, result: InstallResult) -> None:
        pass

    def on_install_skipped(self, result: InstallResult) -> None:
        pass

    def on_install_failed(self, result: InstallResult) -> None:
        pass

    def on_check_complete(self, result: CheckResult) -> None:
        pass
