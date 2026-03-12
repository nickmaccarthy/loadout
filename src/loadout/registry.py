"""Adapter registry for managing agent adapters."""

from __future__ import annotations

from loadout.adapters._protocol import AgentAdapter
from loadout.adapters.claude import ClaudeCodeAdapter
from loadout.adapters.cursor import CursorAdapter
from loadout.adapters.opencode import OpenCodeAdapter
from loadout.exceptions import AdapterAlreadyRegisteredError, AdapterNotFoundError


class AdapterRegistry:
    """Registry of agent adapters.

    Manages the mapping of agent names to their adapter implementations.
    Supports registration of custom adapters for new agents.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, AgentAdapter] = {}

    def register(self, adapter: AgentAdapter, replace: bool = False) -> None:
        """Register an adapter.

        Args:
            adapter: The adapter instance to register.
            replace: If True, replace an existing adapter. Otherwise raise.
        """
        if adapter.agent_name in self._adapters and not replace:
            raise AdapterAlreadyRegisteredError(adapter.agent_name)
        self._adapters[adapter.agent_name] = adapter

    def get(self, agent_name: str) -> AgentAdapter:
        """Get an adapter by agent name.

        Raises AdapterNotFoundError if no adapter is registered.
        """
        if agent_name not in self._adapters:
            raise AdapterNotFoundError(agent_name)
        return self._adapters[agent_name]

    def all(self) -> list[AgentAdapter]:
        """Return all registered adapters."""
        return list(self._adapters.values())

    def names(self) -> list[str]:
        """Return all registered agent names."""
        return list(self._adapters.keys())

    def has(self, agent_name: str) -> bool:
        """Check if an adapter is registered for the given agent."""
        return agent_name in self._adapters


def get_default_registry() -> AdapterRegistry:
    """Create a registry with all built-in adapters."""
    registry = AdapterRegistry()
    registry.register(ClaudeCodeAdapter())
    registry.register(CursorAdapter())
    registry.register(OpenCodeAdapter())
    return registry
