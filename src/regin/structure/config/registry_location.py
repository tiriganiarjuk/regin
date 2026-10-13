"""Where the tool registry and its schema live, relative to the ai workspace root.

The registry is deployment configuration (nornir's), not a per-run argument,
so its location is a typed default here rather than a CLI parameter. The
workspace root itself is resolved at the IO boundary (logic/impure/registry).
"""

from pydantic import BaseModel, ConfigDict


class RegistryLocation(BaseModel):
    model_config = ConfigDict(frozen=True)

    registry_path: str = "smidja/nornir/tool_registry.toml"
    schema_dir: str = "smidja/nornir/schemas/tools"
    schema_name: str = "tool-registry"
