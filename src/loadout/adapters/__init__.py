"""Built-in agent adapters."""

from loadout.adapters._protocol import AgentAdapter
from loadout.adapters.claude import ClaudeCodeAdapter
from loadout.adapters.cursor import CursorAdapter
from loadout.adapters.opencode import OpenCodeAdapter

__all__ = [
    "AgentAdapter",
    "ClaudeCodeAdapter",
    "CursorAdapter",
    "OpenCodeAdapter",
]
