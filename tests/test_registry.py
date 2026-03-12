"""Tests for adapter registry."""

import pytest

from loadout.adapters.claude import ClaudeCodeAdapter
from loadout.adapters.cursor import CursorAdapter
from loadout.exceptions import AdapterAlreadyRegisteredError, AdapterNotFoundError
from loadout.registry import AdapterRegistry, get_default_registry


class TestAdapterRegistry:
    def test_register_and_get(self):
        registry = AdapterRegistry()
        adapter = ClaudeCodeAdapter()
        registry.register(adapter)
        assert registry.get("claude") is adapter

    def test_duplicate_registration_raises(self):
        registry = AdapterRegistry()
        registry.register(ClaudeCodeAdapter())
        with pytest.raises(AdapterAlreadyRegisteredError):
            registry.register(ClaudeCodeAdapter())

    def test_replace_registration(self):
        registry = AdapterRegistry()
        adapter1 = ClaudeCodeAdapter()
        adapter2 = ClaudeCodeAdapter()
        registry.register(adapter1)
        registry.register(adapter2, replace=True)
        assert registry.get("claude") is adapter2

    def test_get_missing_raises(self):
        registry = AdapterRegistry()
        with pytest.raises(AdapterNotFoundError):
            registry.get("nonexistent")

    def test_all(self):
        registry = AdapterRegistry()
        registry.register(ClaudeCodeAdapter())
        registry.register(CursorAdapter())
        assert len(registry.all()) == 2

    def test_names(self):
        registry = AdapterRegistry()
        registry.register(ClaudeCodeAdapter())
        registry.register(CursorAdapter())
        names = registry.names()
        assert "claude" in names
        assert "cursor" in names

    def test_has(self):
        registry = AdapterRegistry()
        registry.register(ClaudeCodeAdapter())
        assert registry.has("claude") is True
        assert registry.has("nonexistent") is False


class TestGetDefaultRegistry:
    def test_has_all_built_in_adapters(self):
        registry = get_default_registry()
        assert registry.has("claude")
        assert registry.has("cursor")
        assert registry.has("opencode")
        assert len(registry.all()) == 3
