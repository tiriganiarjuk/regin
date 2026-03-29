"""Tool registry loader — the non-gate IO boundary for L8.

CC=1-3. Impure — reads TOML from disk.

The tool registry is external configuration (not a pipeline checkpoint) that
maps output specifications to tool binaries. The registry lives in the nornir
project (not regin) because tool binaries are deployment-specific, not
definition-specific — the same agent definition should resolve to different
tool binaries depending on the deployment environment.

This is the only non-gate IO operation in L8. All other IO in the pipeline
goes through gate modules.
"""

import tomllib
from pathlib import Path

from regin.structure.config.tool_registry import ToolRegistryEntry

REGISTRY_PATH = Path.home() / ".ai" / "smidja" / "nornir" / "tool_registry.toml"


def load_registry(path: Path = REGISTRY_PATH) -> list[ToolRegistryEntry]:
    """Load tool registry entries from TOML. Default path points to nornir's registry.

    Returns a list of ToolRegistryEntry models, each describing one output tool
    binary with its matching criteria (format, write frequency, paths) and
    invocation details (binary name, invocation template).
    """
    with path.open("rb") as file_handle:
        data = tomllib.load(file_handle)
    return [ToolRegistryEntry.model_validate(entry) for entry in data["tools"]]
