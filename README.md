# loadout

Install artifacts (skills, rules, agents, commands) into coding agents.

**loadout** is a Python library that other CLIs import to install artifacts into coding agents like Claude Code, Cursor, and OpenCode. It extracts the "copy skills to agent config" logic into a reusable, agent-agnostic library with an extensible adapter pattern.

## Quick Start

```bash
pip install loadout
```

### Three UX Tiers

```python
from pathlib import Path
from loadout import install_all, install_interactive, install, discover_artifacts, detect_agents

skills_dir = Path("./my-skills")

# 1. Yolo mode - install everything to all detected agents
summary = install_all(skills_dir, force=True)

# 2. Interactive - checkbox prompt for agent selection (requires loadout[interactive])
summary = install_interactive(skills_dir)

# 3. Headless API - full control
artifacts = discover_artifacts(skills_dir)
agents = detect_agents()
summary = install(artifacts, agents, force=True)

print(f"Installed: {len(summary.installed)}")
print(f"Skipped: {len(summary.skipped)}")
print(f"Failed: {len(summary.failed)}")
```

## Supported Agents

| Agent | Skills | Rules | Agents | Commands |
|-------|--------|-------|--------|----------|
| Claude Code (`~/.claude/`) | Yes | Yes | Yes | Yes |
| Cursor (`~/.cursor/`) | Yes | Yes (.mdc) | -- | -- |
| OpenCode (`~/.opencode/`) | Yes | -- | -- | Yes |

## Artifact Discovery

Artifacts are discovered by scanning for marker files:

```
my-skills/
  login-skill/
    SKILL.md          # Marker file (also contains the skill content)
    helper.py
  security/
    auth-rule/
      RULE.md         # Marker file for a rule
```

Or use a `loadout.yaml` manifest for explicit control:

```yaml
artifacts:
  - name: login-skill
    type: skill
    path: login-skill
  - name: auth-rule
    type: rule
    path: security/auth-rule/RULE.md
    category: security
```

## Custom Adapters

Register adapters for new agents:

```python
from loadout import AgentAdapter, AdapterRegistry, get_default_registry

class MyAgentAdapter(AgentAdapter):
    # Implement the abstract methods...
    pass

registry = get_default_registry()
registry.register(MyAgentAdapter())

# Use with install functions
summary = install_all(skills_dir, registry=registry)
```

## Lifecycle Callbacks

CLIs can hook into installation events:

```python
from loadout import LoadoutCallbacks, Artifact, DetectedAgent, InstallResult, install_all

class MyCallbacks:
    def on_artifact_discovered(self, artifact: Artifact) -> None:
        print(f"Found: {artifact.name}")

    def on_install_complete(self, result: InstallResult) -> None:
        print(f"Installed {result.artifact.name} to {result.agent.display_name}")

    def on_install_failed(self, result: InstallResult) -> None:
        print(f"Failed: {result.error}")

    # Implement remaining hooks as no-ops...
    def on_agent_detected(self, agent: DetectedAgent) -> None: pass
    def on_install_started(self, artifact: Artifact, agent: DetectedAgent) -> None: pass
    def on_install_skipped(self, result: InstallResult) -> None: pass

summary = install_all("./skills", callbacks=MyCallbacks())
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev,interactive]"

# Run tests
pytest

# Type check
mypy src/

# Lint
ruff check src/
```
