"""Load tool_registry.toml into typed models.

The one impure boundary for L8 beyond gates.
"""

import tomllib
from pathlib import Path

from regin.structures.tool_registry import ToolRegistryEntry

REGISTRY_PATH = Path(__file__).parents[4] / "tool_registry.toml"


def load_registry(path: Path = REGISTRY_PATH) -> list[ToolRegistryEntry]:
    """Load tool registry entries from TOML."""
    with path.open("rb") as f:
        data = tomllib.load(f)
    return [ToolRegistryEntry.model_validate(entry) for entry in data["tools"]]
