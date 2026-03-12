# 🎒 loadout

**The package manager for AI coding agent artifacts.**

Stop manually copying skills, rules, agents, and commands into every coding agent's config directory. **loadout** handles discovery, transformation, and installation across Claude Code, Cursor, and OpenCode — so your CLI or project setup script doesn't have to.

## 📦 Installation

```bash
# uv (recommended)
uv add loadout

# pip
pip install loadout

# With interactive agent selection prompt
uv add "loadout[interactive]"
pip install "loadout[interactive]"
```

---

## 🤔 Why loadout?

Every team building on top of AI coding agents hits the same problem: distributing custom skills, rules, and commands to developers' machines. The config directories differ, the file formats differ, and the logic for "install this skill to that agent" gets copy-pasted across tooling.

**loadout** extracts that logic into a single, typed, tested library with an extensible adapter pattern. You write your artifacts once. loadout puts them where they belong.

- 🌐 **Agent-agnostic** — one artifact definition works across all supported agents
- 🔍 **Auto-detection** — discovers which agents are installed on the system
- 📁 **Convention + configuration** — scan for marker files, or define a manifest
- 🔌 **Adapter pattern** — add support for new agents without touching core logic
- 🪝 **Lifecycle hooks** — plug in your own logging, progress bars, or analytics
- 🛡️ **Fully typed** — strict mypy, Pydantic models, protocol classes

---

## ⚡ Quick start

### 🚀 Install everything to every detected agent

```python
from loadout import install_all

summary = install_all("./my-artifacts", force=True)

print(f"✅ Installed: {len(summary.installed)}")
print(f"⏭️  Skipped:   {len(summary.skipped)}")
print(f"❌ Failed:    {len(summary.failed)}")
```

### 💬 Interactive mode (checkbox prompt)

```bash
uv add "loadout[interactive]"
```

```python
from loadout import install_interactive

summary = install_interactive("./my-artifacts")
```

### 🎛️ Full control

```python
from loadout import discover_artifacts, detect_agents, install

artifacts = discover_artifacts("./my-artifacts")
agents = detect_agents()
summary = install(artifacts, agents, force=True)
```

Three tiers — pick the one that fits your UX. 🎯

---

## 🤖 Supported agents

| Agent | Config dir | Skills | Rules | Agents | Commands |
|---|---|---|---|---|---|
| **Claude Code** | `~/.claude/` | ✅ | ✅ | ✅ | ✅ |
| **Cursor** | `~/.cursor/` | ✅ | ✅ (.mdc) | — | — |
| **OpenCode** | `~/.opencode/` | ✅ | — | — | ✅ |

loadout auto-detects which agents are present and only installs to agents that support each artifact type. Unsupported combinations are cleanly skipped. ✨

---

## 🔎 Artifact discovery

### 📂 Convention-based (marker files)

Drop marker files into your artifact directories and loadout will find them:

```text
my-artifacts/
  login-skill/
    SKILL.md              # ← marker: this directory is a skill
    helper.py
    utils.py
  security/
    auth-rule/
      RULE.md             # ← marker: this file is a rule
  setup-agent/
    AGENT.md              # ← marker: this file is an agent
  deploy/
    COMMAND.md            # ← marker: this file is a command
```

Marker files double as the artifact content — the `SKILL.md` **is** the skill. Categories are derived from directory structure (`security/auth-rule/` → category `security`).

### 📋 Manifest-based (loadout.yaml)

For explicit control, add a `loadout.yaml` to the root of your artifacts directory:

```yaml
artifacts:
  - name: login-skill
    type: skill
    path: login-skill

  - name: auth-rule
    type: rule
    path: security/auth-rule/RULE.md
    category: security
    description: "Enforces authentication checks"
```

When a manifest is present, marker-file scanning is skipped entirely — you have full control over what gets installed.

### 📝 Frontmatter support

Artifact files can include YAML frontmatter for metadata:

```markdown
---
description: Handles user login flows
globs:
  - "src/auth/**"
always_apply: true
---

# Login Skill

Your skill content here...
```

---

## 🔌 Custom adapters

Need to support a new coding agent? Implement the `AgentAdapter` interface and register it:

```python
from pathlib import Path
from loadout import (
    AgentAdapter,
    Artifact,
    ArtifactType,
    DetectedAgent,
    InstallResult,
    get_default_registry,
    install_all,
)

class WindsurfAdapter(AgentAdapter):
    @property
    def agent_name(self) -> str:
        return "windsurf"

    @property
    def display_name(self) -> str:
        return "Windsurf"

    @property
    def config_dir_name(self) -> str:
        return ".windsurf"

    def supported_artifact_types(self) -> set[ArtifactType]:
        return {ArtifactType.SKILL, ArtifactType.RULE}

    def detect(self) -> DetectedAgent | None:
        config_dir = Path.home() / self.config_dir_name
        if config_dir.is_dir():
            return DetectedAgent(
                name=self.agent_name,
                config_dir=config_dir,
                display_name=self.display_name,
            )
        return None

    def get_target_path(self, artifact: Artifact, config_dir: Path) -> Path:
        # Your path resolution logic
        ...

    def transform_content(self, artifact: Artifact, content: str) -> str:
        # Your content transformation logic
        return content

    def transform_filename(self, artifact: Artifact, filename: str) -> str:
        return filename

    def install(self, artifact: Artifact, agent: DetectedAgent, force: bool = False) -> InstallResult:
        # Your install logic
        ...

# Register and use 🎉
registry = get_default_registry()
registry.register(WindsurfAdapter())

summary = install_all("./my-artifacts", registry=registry)
```

The adapter pattern means core loadout never needs to change when new agents appear. 🧩

---

## 🪝 Lifecycle callbacks

Hook into every stage of the installation process for logging, progress bars, analytics, or custom error handling:

```python
from loadout import LoadoutCallbacks, Artifact, DetectedAgent, InstallResult, install_all

class RichCallbacks:
    """Example: pretty-print progress with Rich."""

    def on_artifact_discovered(self, artifact: Artifact) -> None:
        print(f"  🔎 Found {artifact.artifact_type.value}: {artifact.name}")

    def on_agent_detected(self, agent: DetectedAgent) -> None:
        print(f"  🤖 Detected agent: {agent.display_name}")

    def on_install_started(self, artifact: Artifact, agent: DetectedAgent) -> None:
        print(f"  ⏳ Installing {artifact.name} → {agent.display_name}...")

    def on_install_complete(self, result: InstallResult) -> None:
        print(f"  ✅ Installed to {result.target_path}")

    def on_install_skipped(self, result: InstallResult) -> None:
        print(f"  ⏭️  Skipped: {result.error}")

    def on_install_failed(self, result: InstallResult) -> None:
        print(f"  💥 FAILED: {result.error}")

summary = install_all("./my-artifacts", callbacks=RichCallbacks())
```

Only override the hooks you care about — the `LoadoutCallbacks` protocol defines the full interface, and `NoOpCallbacks` provides a ready-made base with no-op defaults.

---

## 📖 API reference

### ⚙️ Top-level functions

| Function | Description |
|---|---|
| `install_all(source_dir, force, registry, callbacks)` | Discover artifacts, detect agents, install everything |
| `install_interactive(source_dir, force, registry, callbacks)` | Same as above with interactive agent selection |
| `install(artifacts, agents, force, registry, callbacks)` | Install specific artifacts to specific agents |
| `discover_artifacts(source_dir)` | Scan a directory and return a list of `Artifact` objects |
| `detect_agents(registry)` | Detect installed coding agents |
| `get_default_registry()` | Get the built-in adapter registry |

### 🧱 Models

| Model | Description |
|---|---|
| `Artifact` | A discovered artifact (name, type, source path, category, frontmatter) |
| `ArtifactType` | Enum: `SKILL`, `RULE`, `AGENT`, `COMMAND` |
| `DetectedAgent` | An agent found on the system (name, config dir, display name) |
| `InstallResult` | Result of a single artifact install (status, target path, error) |
| `InstallSummary` | Batch result with `.installed`, `.skipped`, `.failed`, `.already_existed` |
| `Manifest` | Parsed `loadout.yaml` manifest |

### 🚨 Exceptions

| Exception | Description |
|---|---|
| `LoadoutError` | Base exception for all loadout errors |
| `ArtifactNotFoundError` | Source artifact path does not exist |
| `ManifestError` | Invalid `loadout.yaml` |
| `InstallError` | Installation failed |
| `AdapterNotFoundError` | No adapter registered for the given agent |
| `AdapterAlreadyRegisteredError` | Adapter name collision |
| `TransformError` | Content transformation failed |

---

## 🛠️ Development

```bash
# Clone and install with all extras
git clone https://github.com/nickmaccarthy/loadout.git
cd loadout

# uv (recommended)
uv sync --all-extras

# pip
pip install -e ".[dev,interactive]"

# Set up pre-commit hooks
uv run pre-commit install

# Run all pre-commit checks (ruff, mypy, formatting, etc.)
uv run pre-commit run --all-files

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=loadout --cov-report=term-missing
```

> 💡 **Pre-commit hooks** run automatically on every `git commit`, catching lint errors, type issues, and formatting problems before they hit CI.

---

## 📋 Requirements

- 🐍 Python 3.10+
- [pydantic](https://docs.pydantic.dev/) >= 2.0
- [PyYAML](https://pyyaml.org/) >= 6.0
- [questionary](https://questionary.readthedocs.io/) >= 2.0 *(optional, for interactive mode)*

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
