"""Built-in interactive prompts (requires questionary)."""

from __future__ import annotations

from loadout.models import DetectedAgent


def prompt_agent_selection(agents: list[DetectedAgent]) -> list[DetectedAgent]:
    """Present a checkbox prompt for agent selection.

    Requires the `questionary` package (install with `loadout[interactive]`).

    Args:
        agents: Available agents to choose from.

    Returns:
        List of selected agents.

    Raises:
        ImportError: If questionary is not installed.
    """
    try:
        import questionary
    except ImportError:
        raise ImportError(
            "questionary is required for interactive prompts. "
            "Install it with: pip install loadout[interactive]"
        ) from None

    choices = [
        questionary.Choice(
            title=agent.display_name or agent.name,
            value=agent,
            checked=True,
        )
        for agent in agents
    ]

    selected = questionary.checkbox(
        "Select agents to install to:",
        choices=choices,
    ).ask()

    return selected or []
