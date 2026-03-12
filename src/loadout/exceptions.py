"""Custom exceptions for loadout."""


class LoadoutError(Exception):
    """Base exception for all loadout errors."""


class AdapterNotFoundError(LoadoutError):
    """Raised when no adapter is found for a given agent."""

    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name
        super().__init__(f"No adapter registered for agent: {agent_name}")


class AdapterAlreadyRegisteredError(LoadoutError):
    """Raised when attempting to register an adapter for an already-registered agent."""

    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name
        super().__init__(f"Adapter already registered for agent: {agent_name}")


class ArtifactNotFoundError(LoadoutError):
    """Raised when an artifact path does not exist."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Artifact not found: {path}")


class ManifestError(LoadoutError):
    """Raised when a loadout.yaml manifest is invalid."""


class TransformError(LoadoutError):
    """Raised when content transformation fails."""


class InstallError(LoadoutError):
    """Raised when artifact installation fails."""
