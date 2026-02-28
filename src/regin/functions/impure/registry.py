"""Load the tool registry from tool_registry.toml.

Reads once at import time. The registry is a tuple of frozen entries
describing every deployed Nornir writer tool.

TODO: Auto-generate tool_registry.toml from Nornir on rebuild.
"""

import tomllib
from pathlib import Path

from regin.structures.tool_registry import ToolRegistryEntry


def load_tool_registry() -> tuple[ToolRegistryEntry, ...]:
    """Load tool registry from tool_registry.toml at the project root."""
    registry_path = Path(__file__).parents[4] / "tool_registry.toml"
    with registry_path.open("rb") as toml_file:
        data = tomllib.load(toml_file)
    return tuple(
        ToolRegistryEntry.model_validate(entry)
        for entry in data.get("tools", [])
    )


TOOL_REGISTRY: tuple[ToolRegistryEntry, ...] = load_tool_registry()
